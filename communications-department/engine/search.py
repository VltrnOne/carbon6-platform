"""Search Engine - Cross-channel communication search."""
import logging

log = logging.getLogger("hermes.search")


class SearchEngine:
    """Full-text search across all communication channels."""

    def __init__(self, db, email_engine=None):
        self.db = db
        self.email_engine = email_engine

    def search(self, query: str, channel: str = None,
               contact: str = None, limit: int = 50) -> dict:
        """Search across all channels.

        Args:
            query: Search text
            channel: Filter to specific channel (sms, email, voice)
            contact: Filter to specific contact (name, phone, email)
            limit: Max results
        """
        contact_id = None
        contact_info = None
        if contact:
            contact_info = self.db.resolve_contact(contact)
            if contact_info:
                contact_id = contact_info["id"]

        # Search local message database
        db_results = self.db.search_messages(
            query=query, channel=channel,
            contact_id=contact_id, limit=limit,
        )

        # Also search IMAP if email channel and engine available
        imap_results = []
        if (not channel or channel == "email") and self.email_engine and self.email_engine.can_receive:
            imap_results = self.email_engine.search_emails(query, limit=10)
            # Filter out errors
            imap_results = [r for r in imap_results if "error" not in r]

        return {
            "query": query,
            "channel_filter": channel,
            "contact_filter": contact_info,
            "results": db_results,
            "imap_results": imap_results,
            "total": len(db_results) + len(imap_results),
        }
