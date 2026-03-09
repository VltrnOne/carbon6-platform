"""Message Router - Intelligent routing and priority queuing via Redis."""
import json
import logging
import redis

from ..config.settings import load_config

log = logging.getLogger("hermes.router")


class MessageRouter:
    """Routes messages to the appropriate channel with priority queuing."""

    PRIORITY_HIGH = 1
    PRIORITY_NORMAL = 5
    PRIORITY_LOW = 10

    def __init__(self, db, sms_engine=None, email_engine=None, voice_engine=None, imessage_engine=None):
        self.db = db
        self.sms = sms_engine
        self.email = email_engine
        self.voice = voice_engine
        self.imessage = imessage_engine
        config = load_config().redis
        self.redis = redis.Redis(
            host=config.host, port=config.port, db=config.db,
            decode_responses=True,
        )
        self.queue_key = f"{config.prefix}queue"

    def route(self, to: str, body: str, channel: str = None,
              subject: str = None, contact_id: int = None,
              priority: int = PRIORITY_NORMAL) -> dict:
        """Route a message to the best channel.

        If channel is not specified, auto-detect based on contact preference.
        """
        # Auto-detect channel
        if not channel:
            channel = self._detect_channel(to, contact_id)

        # Queue or send directly based on priority
        if priority <= self.PRIORITY_HIGH:
            return self._send_direct(channel, to, body, subject, contact_id)
        else:
            return self._enqueue(channel, to, body, subject, contact_id, priority)

    def _detect_channel(self, to: str, contact_id: int = None) -> str:
        """Auto-detect the best channel for a recipient."""
        if contact_id:
            contact = self.db.get_contact(contact_id=contact_id)
            if contact:
                return contact.get("preferred_channel", "sms")

        if "@" in to:
            return "email"
        if to.startswith("+") or to.replace("-", "").replace(" ", "").isdigit():
            return "sms"
        # Try to resolve by name
        contact = self.db.resolve_contact(to)
        if contact:
            return contact.get("preferred_channel", "sms")
        return "sms"

    def _send_direct(self, channel: str, to: str, body: str,
                     subject: str = None, contact_id: int = None) -> dict:
        """Send immediately without queuing."""
        # iMessage is preferred for text messages (sends from your actual phone)
        if channel in ("sms", "imessage", "text"):
            if self.imessage and self.imessage.is_configured:
                return self.imessage.send(to, body, contact_id=contact_id)
            if self.sms and self.sms.is_configured:
                return self.sms.send(to, body, contact_id=contact_id)
            return {"error": "No text channel configured (iMessage or Twilio SMS)"}
        elif channel == "email" and self.email:
            return self.email.send(to, subject or "Message from Carbon6", body, contact_id=contact_id)
        elif channel == "voice" and self.voice:
            return self.voice.call(to, message=body, contact_id=contact_id)
        return {"error": f"No engine configured for channel: {channel}"}

    def _enqueue(self, channel: str, to: str, body: str,
                 subject: str = None, contact_id: int = None,
                 priority: int = PRIORITY_NORMAL) -> dict:
        """Add to Redis priority queue for async processing."""
        msg = json.dumps({
            "channel": channel, "to": to, "body": body,
            "subject": subject, "contact_id": contact_id,
        })
        try:
            self.redis.zadd(self.queue_key, {msg: priority})
            return {"status": "queued", "channel": channel, "to": to, "priority": priority}
        except Exception as e:
            log.warning(f"Redis queue failed, sending direct: {e}")
            return self._send_direct(channel, to, body, subject, contact_id)

    def process_queue(self, batch_size: int = 10) -> list:
        """Process queued messages (called by worker)."""
        results = []
        messages = self.redis.zpopmin(self.queue_key, batch_size)
        for msg_json, _score in messages:
            msg = json.loads(msg_json)
            result = self._send_direct(
                msg["channel"], msg["to"], msg["body"],
                msg.get("subject"), msg.get("contact_id"),
            )
            results.append(result)
        return results

    def queue_size(self) -> int:
        """Get number of messages in queue."""
        try:
            return self.redis.zcard(self.queue_key)
        except Exception:
            return 0
