"""iMessage Bridge Engine - Send/receive iMessages via iPhone Shortcuts + Pushcut.

Architecture:
  OUTBOUND: HERMES → Pushcut API → iPhone Shortcut → Messages.app → iMessage
  INBOUND:  Messages.app → Shortcut automation → HERMES webhook → DB

Pushcut Automation Server runs on the iPhone and listens for webhook triggers.
Each trigger executes an Apple Shortcut that performs the actual send.
"""
import json
import logging
import os
import sys
import time
from typing import Optional

import redis
import requests

from ..config.settings import load_config

# Add vault to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
try:
    from lib.vault import get_secret
except ImportError:
    def get_secret(key, default=""):
        return os.getenv(key, default)

log = logging.getLogger("hermes.imessage")


class IMessageEngine:
    """Send and receive iMessages through iPhone via Pushcut bridge."""

    # Pushcut API
    PUSHCUT_API = "https://api.pushcut.io"

    def __init__(self, db=None):
        self.db = db
        self.api_key = get_secret("PUSHCUT_API_KEY")
        self.device_name = get_secret("PUSHCUT_DEVICE_NAME")
        # Shortcut names on the iPhone
        self.send_shortcut = get_secret("IMESSAGE_SEND_SHORTCUT", "HERMES Send Message")
        self.config = load_config()

        # Redis for outbound queue (messages waiting for phone to pick up)
        try:
            redis_pw = None
            try:
                with open('/root/.redis_password', 'r') as f:
                    redis_pw = f.read().strip()
            except Exception:
                pass
            self.redis = redis.Redis(
                host=self.config.redis.host,
                port=self.config.redis.port,
                db=self.config.redis.db,
                decode_responses=True,
                password=redis_pw,
            )
        except Exception:
            self.redis = None

        self.queue_key = f"{self.config.redis.prefix}imessage:outbound"
        self.retry_key = f"{self.config.redis.prefix}imessage:retry"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.device_name)

    def send(self, to: str, body: str, contact_id: int = None) -> dict:
        """Send an iMessage via Pushcut → Shortcut → Messages.app.

        Args:
            to: Phone number or contact name
            body: Message text
            contact_id: Optional DB contact ID
        """
        if not self.is_configured:
            return {
                "error": "iMessage bridge not configured. Set PUSHCUT_API_KEY and PUSHCUT_DEVICE_NAME.",
                "setup": "Run: hermes setup-imessage"
            }

        # Resolve contact name to phone if needed
        resolved_to = to
        if self.db and not (to.startswith("+") or to.replace("-", "").isdigit()):
            contact = self.db.resolve_contact(to)
            if contact:
                resolved_to = contact.get("phone", to)
                contact_id = contact.get("id", contact_id)

        # Build Pushcut payload
        payload = {
            "to": resolved_to,
            "body": body,
            "timestamp": time.time(),
        }

        try:
            result = self._trigger_pushcut(payload)

            # Store in DB
            if self.db:
                self.db.store_message(
                    channel="imessage",
                    direction="outbound",
                    from_addr="me",
                    to_addr=resolved_to,
                    body=body,
                    contact_id=contact_id,
                    status="sent" if "error" not in result else "failed",
                    metadata={"bridge": "pushcut", "pushcut_response": result},
                )

            log.info(f"iMessage sent to {resolved_to} via Pushcut")
            return {
                "status": "sent",
                "channel": "imessage",
                "to": resolved_to,
                "body": body,
                "bridge": "pushcut",
                **result,
            }

        except requests.exceptions.ConnectionError:
            # Phone might be offline — queue for retry
            return self._queue_for_retry(payload, contact_id, "Connection failed - phone may be offline")

        except requests.exceptions.Timeout:
            return self._queue_for_retry(payload, contact_id, "Timeout - phone may be asleep")

        except Exception as e:
            log.error(f"iMessage send failed: {e}")
            return {"error": str(e), "channel": "imessage"}

    def _trigger_pushcut(self, payload: dict) -> dict:
        """Trigger the Pushcut Automation Server to run the send Shortcut.

        Pushcut Automation Server endpoint format:
          POST https://api.pushcut.io/{secret}/execute?shortcut=Name
          Body: input JSON passed to the shortcut
        """
        url = f"{self.PUSHCUT_API}/{self.api_key}/execute"

        params = {
            "shortcut": self.send_shortcut,
        }

        response = requests.post(
            url,
            params=params,
            json={"input": json.dumps(payload)},
            timeout=30,
        )

        if response.status_code == 200:
            return response.json() if response.text else {"status": "triggered"}
        else:
            return {
                "error": f"Pushcut API returned {response.status_code}",
                "detail": response.text[:200],
            }

    def _queue_for_retry(self, payload: dict, contact_id: int = None,
                          reason: str = "") -> dict:
        """Queue message for retry when phone comes back online."""
        if self.redis:
            msg = json.dumps({**payload, "contact_id": contact_id, "queued_reason": reason})
            self.redis.rpush(self.queue_key, msg)
            queue_len = self.redis.llen(self.queue_key)
            log.info(f"iMessage queued for retry ({queue_len} in queue): {reason}")
            return {
                "status": "queued",
                "channel": "imessage",
                "reason": reason,
                "queue_position": queue_len,
            }
        return {"error": reason, "channel": "imessage"}

    def process_inbound(self, from_number: str, body: str,
                        is_imessage: bool = True) -> dict:
        """Process an inbound iMessage received via Shortcut → webhook.

        Called when the iPhone Shortcuts automation fires on receiving a message
        and hits our webhook endpoint.
        """
        contact = None
        contact_id = None
        if self.db:
            contact = self.db.get_contact(phone=from_number)
            contact_id = contact["id"] if contact else None

            self.db.store_message(
                channel="imessage" if is_imessage else "sms",
                direction="inbound",
                from_addr=from_number,
                to_addr="me",
                body=body,
                contact_id=contact_id,
                status="received",
                metadata={"is_imessage": is_imessage, "bridge": "shortcuts"},
            )

        log.info(f"Inbound {'iMessage' if is_imessage else 'SMS'} from {from_number}")
        return {
            "status": "received",
            "from": from_number,
            "body": body,
            "contact": contact,
            "is_imessage": is_imessage,
        }

    def retry_queued(self) -> list:
        """Retry all queued messages (called by worker when phone is back)."""
        if not self.redis:
            return []

        results = []
        while True:
            msg_json = self.redis.lpop(self.queue_key)
            if not msg_json:
                break
            msg = json.loads(msg_json)
            result = self.send(msg["to"], msg["body"], contact_id=msg.get("contact_id"))
            results.append(result)

        if results:
            log.info(f"Retried {len(results)} queued iMessages")
        return results

    def queue_size(self) -> int:
        """Number of messages waiting in retry queue."""
        if self.redis:
            return self.redis.llen(self.queue_key)
        return 0

    def status(self) -> dict:
        """Check bridge status."""
        result = {
            "configured": self.is_configured,
            "device": self.device_name or "not set",
            "send_shortcut": self.send_shortcut,
            "queue_size": self.queue_size(),
        }

        # Ping Pushcut to see if Automation Server is reachable
        if self.is_configured:
            try:
                resp = requests.post(
                    f"{self.PUSHCUT_API}/{self.api_key}/execute",
                    params={"shortcut": "__ping__", "timeout": "nowait"},
                    timeout=5,
                )
                # Any response other than connection error means server is up
                result["pushcut_online"] = "Invalid secret" not in resp.text
                result["pushcut_status"] = resp.status_code
            except Exception:
                result["pushcut_online"] = False

        return result
