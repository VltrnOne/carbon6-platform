"""SMS Engine - Send and receive text messages via Twilio."""
import logging
from typing import Optional

from ..config.settings import load_config

log = logging.getLogger("hermes.sms")


class SMSEngine:
    """Handles SMS/MMS via Twilio REST API."""

    def __init__(self, db=None):
        self.config = load_config().twilio
        self.db = db
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.config.account_sid, self.config.auth_token)
        return self._client

    @property
    def is_configured(self) -> bool:
        return self.config.is_configured

    def send(self, to: str, body: str, media_url: str = None,
             contact_id: int = None) -> dict:
        """Send an SMS/MMS message."""
        if not self.is_configured:
            return {"error": "Twilio not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER"}

        kwargs = {
            "to": to,
            "from_": self.config.phone_number,
            "body": body,
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        try:
            message = self.client.messages.create(**kwargs)
            result = {
                "sid": message.sid,
                "status": message.status,
                "to": to,
                "body": body,
                "channel": "sms",
            }

            # Store in database
            if self.db:
                self.db.store_message(
                    channel="sms", direction="outbound",
                    from_addr=self.config.phone_number, to_addr=to,
                    body=body, contact_id=contact_id,
                    status=message.status, provider_sid=message.sid,
                )

            log.info(f"SMS sent to {to}: {message.sid}")
            return result

        except Exception as e:
            log.error(f"SMS send failed to {to}: {e}")
            if self.db:
                self.db.store_message(
                    channel="sms", direction="outbound",
                    from_addr=self.config.phone_number, to_addr=to,
                    body=body, contact_id=contact_id, status="failed",
                    metadata={"error": str(e)},
                )
            return {"error": str(e)}

    def get_status(self, sid: str) -> dict:
        """Check delivery status of a message."""
        if not self.is_configured:
            return {"error": "Twilio not configured"}
        try:
            msg = self.client.messages(sid).fetch()
            return {"sid": msg.sid, "status": msg.status, "error_code": msg.error_code}
        except Exception as e:
            return {"error": str(e)}

    def get_history(self, limit: int = 20) -> list:
        """Get recent SMS history from Twilio."""
        if not self.is_configured:
            return []
        try:
            messages = self.client.messages.list(limit=limit)
            return [
                {
                    "sid": m.sid, "from": m.from_, "to": m.to,
                    "body": m.body, "status": m.status,
                    "date_sent": m.date_sent.isoformat() if m.date_sent else None,
                    "direction": m.direction,
                }
                for m in messages
            ]
        except Exception as e:
            log.error(f"Failed to fetch SMS history: {e}")
            return []

    def process_inbound(self, from_number: str, body: str,
                        media_urls: list = None) -> dict:
        """Process an inbound SMS (called from webhook)."""
        contact = None
        contact_id = None
        if self.db:
            contact = self.db.get_contact(phone=from_number)
            contact_id = contact["id"] if contact else None
            self.db.store_message(
                channel="sms", direction="inbound",
                from_addr=from_number, to_addr=self.config.phone_number,
                body=body, contact_id=contact_id, status="received",
                metadata={"media_urls": media_urls or []},
            )

        log.info(f"Inbound SMS from {from_number}: {body[:50]}...")
        return {
            "from": from_number,
            "body": body,
            "contact": contact,
            "media_urls": media_urls or [],
        }
