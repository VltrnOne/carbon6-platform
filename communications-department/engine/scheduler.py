"""Message Scheduler - Schedule future and recurring messages."""
import logging
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger("hermes.scheduler")


class MessageScheduler:
    """Schedule messages for future delivery."""

    def __init__(self, db, router=None):
        self.db = db
        self.router = router

    def schedule(self, channel: str, to: str, body: str,
                 send_at: datetime, subject: str = None,
                 contact_id: int = None,
                 recurring_cron: str = None) -> dict:
        """Schedule a message for future delivery."""
        if send_at.tzinfo is None:
            send_at = send_at.replace(tzinfo=timezone.utc)

        if send_at <= datetime.now(timezone.utc):
            # Send immediately if time is in the past
            if self.router:
                return self.router.route(to, body, channel=channel, subject=subject, contact_id=contact_id)
            return {"error": "Send time is in the past and no router available"}

        return self.db.schedule_message(
            channel=channel, to_addr=to, body=body,
            send_at=send_at, subject=subject,
            contact_id=contact_id,
            recurring_cron=recurring_cron,
        )

    def cancel(self, schedule_id: int) -> dict:
        """Cancel a scheduled message."""
        with self.db.get_session() as session:
            from .database import ScheduledMessage
            msg = session.query(ScheduledMessage).filter(ScheduledMessage.id == schedule_id).first()
            if msg:
                msg.status = "cancelled"
                session.commit()
                return {"status": "cancelled", "id": schedule_id}
            return {"error": f"Scheduled message {schedule_id} not found"}

    def process_due(self) -> list:
        """Process all due scheduled messages (called by worker/cron)."""
        pending = self.db.get_pending_scheduled()
        results = []
        for msg in pending:
            if self.router:
                result = self.router.route(
                    msg["to_addr"], msg["body"],
                    channel=msg["channel"], subject=msg.get("subject"),
                    contact_id=msg.get("contact_id"),
                )
                results.append(result)

                # Mark as sent
                with self.db.get_session() as session:
                    from .database import ScheduledMessage
                    sched = session.query(ScheduledMessage).filter(
                        ScheduledMessage.id == msg["id"]
                    ).first()
                    if sched:
                        sched.status = "sent"
                        session.commit()

        return results
