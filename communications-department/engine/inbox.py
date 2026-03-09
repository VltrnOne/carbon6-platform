"""Unified Inbox - Aggregated view of all inbound messages."""
import logging

log = logging.getLogger("hermes.inbox")


class UnifiedInbox:
    """Aggregates inbound messages from all channels."""

    def __init__(self, db, email_engine=None):
        self.db = db
        self.email_engine = email_engine

    def get(self, channel: str = None, unread_only: bool = False,
            limit: int = 50) -> dict:
        """Get unified inbox view."""
        # Get from local database
        messages = self.db.get_inbox(
            channel=channel, unread_only=unread_only, limit=limit,
        )

        unread_count = len([m for m in messages if not m.get("is_read")])

        # Channel breakdown
        by_channel = {"sms": [], "email": [], "voice": []}
        for msg in messages:
            ch = msg.get("channel", "sms")
            if ch in by_channel:
                by_channel[ch].append(msg)

        return {
            "total": len(messages),
            "unread": unread_count,
            "messages": messages,
            "by_channel": {k: len(v) for k, v in by_channel.items()},
        }

    def mark_read(self, message_id: int) -> bool:
        """Mark a message as read."""
        return self.db.mark_read(message_id)

    def mark_all_read(self, channel: str = None) -> int:
        """Mark all messages as read."""
        inbox = self.db.get_inbox(channel=channel, unread_only=True, limit=500)
        count = 0
        for msg in inbox:
            if self.db.mark_read(msg["id"]):
                count += 1
        return count

    def sync_email(self, limit: int = 20) -> dict:
        """Pull latest emails from IMAP into local database."""
        if not self.email_engine or not self.email_engine.can_receive:
            return {"error": "Email receive not configured"}

        emails = self.email_engine.fetch_inbox(limit=limit, unread_only=True)
        return {"synced": len([e for e in emails if "error" not in e])}
