"""Pushcut Bridge - Base class for all device operations.

Every engine inherits this. Provides execute_shortcut() which triggers
Apple Shortcuts on the iPhone via the Pushcut Automation Server.

Flow: Server -> POST Pushcut API -> iPhone Shortcut -> iOS Action -> Result
"""
import json
import logging
import os
import time
from typing import Optional

import redis
import requests

from ..config.settings import load_config

log = logging.getLogger("aegis.bridge")


class PushcutBridge:
    """Execute Apple Shortcuts on iPhone via Pushcut Automation Server."""

    def __init__(self, db=None, subsystem: str = "general"):
        self.db = db
        self.subsystem = subsystem
        self.config = load_config()
        self.api_key = self.config.pushcut.api_key
        self.device_name = self.config.pushcut.device_name
        self.base_url = self.config.pushcut.base_url

        try:
            self.redis = redis.Redis(
                host=self.config.redis.host,
                port=self.config.redis.port,
                db=self.config.redis.db,
                decode_responses=True,
            )
            self.redis.ping()
        except Exception:
            self.redis = None

        self.queue_key = f"{self.config.redis.prefix}{subsystem}:queue"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.device_name)

    def execute_shortcut(self, shortcut_name: str, payload: dict = None,
                         timeout: int = 30, nowait: bool = False) -> dict:
        """Trigger an Apple Shortcut via Pushcut and return its output.

        Args:
            shortcut_name: Name of the Shortcut on the iPhone
            payload: Dict passed as input to the Shortcut
            timeout: HTTP timeout in seconds
            nowait: Fire-and-forget (don't wait for Shortcut result)
        """
        if not self.is_configured:
            return {"error": "Pushcut not configured. Set PUSHCUT_API_KEY and PUSHCUT_DEVICE_NAME."}

        url = f"{self.base_url}/{self.api_key}/execute"
        params = {"shortcut": shortcut_name}
        if nowait:
            params["timeout"] = "nowait"

        body = {}
        if payload:
            body["input"] = json.dumps(payload)

        # Log command to DB
        command_id = None
        if self.db:
            command_id = self.db.store_command(
                subsystem=self.subsystem,
                action=shortcut_name,
                payload=payload or {},
            )

        try:
            resp = requests.post(url, params=params, json=body, timeout=timeout)

            if resp.status_code in (200, 202):
                try:
                    result = resp.json() if resp.text.strip() else {"status": "triggered"}
                except ValueError:
                    result = {"status": "triggered", "raw": resp.text[:500]}
            else:
                result = {
                    "error": f"Pushcut returned {resp.status_code}",
                    "detail": resp.text[:300],
                }

            # Update command in DB
            if self.db and command_id:
                status = "completed" if "error" not in result else "failed"
                self.db.update_command(command_id, status=status, result=result)

            log.info(f"[{self.subsystem}] {shortcut_name} -> {resp.status_code}")
            return result

        except requests.exceptions.ConnectionError:
            return self._queue_for_retry(shortcut_name, payload, command_id,
                                         "Connection failed - phone may be offline")
        except requests.exceptions.Timeout:
            return self._queue_for_retry(shortcut_name, payload, command_id,
                                         "Timeout - phone may be asleep")
        except Exception as e:
            log.error(f"[{self.subsystem}] {shortcut_name} failed: {e}")
            if self.db and command_id:
                self.db.update_command(command_id, status="failed", result={"error": str(e)})
            return {"error": str(e)}

    def _queue_for_retry(self, shortcut_name: str, payload: dict,
                         command_id: int = None, reason: str = "") -> dict:
        if self.db and command_id:
            self.db.update_command(command_id, status="queued", result={"reason": reason})

        if self.redis:
            msg = json.dumps({
                "shortcut": shortcut_name,
                "payload": payload,
                "command_id": command_id,
                "reason": reason,
                "queued_at": time.time(),
            })
            self.redis.rpush(self.queue_key, msg)
            queue_len = self.redis.llen(self.queue_key)
            log.info(f"[{self.subsystem}] Queued for retry ({queue_len} in queue): {reason}")
            return {"status": "queued", "reason": reason, "queue_position": queue_len}

        return {"error": reason}

    def retry_queued(self) -> list:
        """Retry all queued commands."""
        if not self.redis:
            return []

        results = []
        while True:
            msg_json = self.redis.lpop(self.queue_key)
            if not msg_json:
                break
            msg = json.loads(msg_json)
            result = self.execute_shortcut(msg["shortcut"], msg.get("payload"))
            results.append({"shortcut": msg["shortcut"], **result})

        if results:
            log.info(f"[{self.subsystem}] Retried {len(results)} queued commands")
        return results

    def queue_size(self) -> int:
        if self.redis:
            return self.redis.llen(self.queue_key)
        return 0

    def ping(self) -> dict:
        """Check if Pushcut Automation Server is reachable."""
        if not self.is_configured:
            return {"online": False, "reason": "not configured"}

        try:
            resp = requests.post(
                f"{self.base_url}/{self.api_key}/execute",
                params={"shortcut": "__ping__", "timeout": "nowait"},
                timeout=5,
            )
            online = resp.status_code in (200, 202)
            return {
                "online": online,
                "status_code": resp.status_code,
                "device": self.device_name,
            }
        except Exception as e:
            return {"online": False, "reason": str(e)}
