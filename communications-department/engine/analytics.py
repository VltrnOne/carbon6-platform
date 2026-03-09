"""Communication Analytics - Metrics, reports, and insights."""
import logging

log = logging.getLogger("hermes.analytics")


class AnalyticsEngine:
    """Track and report on communication metrics."""

    def __init__(self, db):
        self.db = db

    def dashboard(self, days: int = 30) -> dict:
        """Get analytics dashboard data."""
        stats = self.db.get_message_stats(days=days)
        stats["period_days"] = days
        return stats

    def contact_engagement(self, contact_identifier: str) -> dict:
        """Get engagement metrics for a specific contact."""
        contact = self.db.resolve_contact(contact_identifier)
        if not contact:
            return {"error": f"Contact not found: {contact_identifier}"}

        messages = self.db.get_conversation(contact["id"], limit=500)
        inbound = [m for m in messages if m["direction"] == "inbound"]
        outbound = [m for m in messages if m["direction"] == "outbound"]

        by_channel = {}
        for msg in messages:
            ch = msg["channel"]
            by_channel.setdefault(ch, {"sent": 0, "received": 0})
            if msg["direction"] == "outbound":
                by_channel[ch]["sent"] += 1
            else:
                by_channel[ch]["received"] += 1

        return {
            "contact": contact,
            "total_messages": len(messages),
            "sent": len(outbound),
            "received": len(inbound),
            "by_channel": by_channel,
            "last_message": messages[0] if messages else None,
        }
