"""Campaign Engine - Create, read, send text campaigns to one, group, or all contacts."""
import logging
import time
from datetime import datetime, timezone
from typing import Optional

log = logging.getLogger("hermes.campaign")


class CampaignEngine:
    """Manages text/SMS campaigns with full lifecycle: create → preview → send."""

    # Throttle: messages per second (avoids carrier rate limits)
    THROTTLE_RATE = 1.0  # 1 msg/sec default, adjustable

    def __init__(self, db, contacts, router):
        self.db = db
        self.contacts = contacts
        self.router = router

    def create(self, name: str, body: str, target_type: str,
               target_value: str = None, channel: str = "sms",
               subject: str = None, template_id: int = None,
               scheduled_at: datetime = None) -> dict:
        """Create a new campaign (draft or scheduled).

        target_type: 'single' (one contact), 'group', 'tag', 'all'
        target_value: contact name/id for single, group name for group, tag for tag, None for all
        """
        if target_type not in ("single", "group", "tag", "all"):
            return {"error": f"Invalid target_type: {target_type}. Use: single, group, tag, all"}

        # Validate target exists
        recipients = self._resolve_recipients(target_type, target_value)
        if not recipients:
            return {"error": f"No contacts found for {target_type}={target_value or 'all'}"}

        campaign = self.db.create_campaign(
            name=name, body=body, target_type=target_type,
            target_value=target_value, channel=channel,
            subject=subject, template_id=template_id,
            scheduled_at=scheduled_at,
        )

        # Pre-populate recipients
        for contact in recipients:
            self.db.add_campaign_recipient(campaign["id"], contact["id"])

        campaign["total_recipients"] = len(recipients)
        self.db.update_campaign(campaign["id"], total_recipients=len(recipients))

        log.info(f"Campaign '{name}' created → {len(recipients)} recipients [{target_type}]")
        return campaign

    def read(self, campaign_id: int) -> Optional[dict]:
        """Read campaign details with recipient breakdown."""
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        recipients = self.db.get_campaign_recipients(campaign_id)
        campaign["recipients"] = recipients
        campaign["stats"] = {
            "pending": sum(1 for r in recipients if r["status"] == "pending"),
            "sent": sum(1 for r in recipients if r["status"] == "sent"),
            "delivered": sum(1 for r in recipients if r["status"] == "delivered"),
            "failed": sum(1 for r in recipients if r["status"] == "failed"),
            "skipped": sum(1 for r in recipients if r["status"] == "skipped"),
        }
        return campaign

    def list(self, status: str = None) -> dict:
        """List all campaigns, optionally filtered by status."""
        campaigns = self.db.list_campaigns(status=status)
        return {"campaigns": campaigns, "total": len(campaigns)}

    def preview(self, campaign_id: int) -> dict:
        """Preview a campaign - show who will receive it and the message."""
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        recipients = self.db.get_campaign_recipients(campaign_id)
        contact_names = []
        for r in recipients:
            contact = self.db.get_contact(contact_id=r["contact_id"])
            if contact:
                contact_names.append({
                    "name": contact["name"],
                    "phone": contact.get("phone"),
                    "email": contact.get("email"),
                    "channel": campaign["channel"],
                })

        return {
            "campaign": campaign["name"],
            "message": campaign["body"],
            "channel": campaign["channel"],
            "subject": campaign.get("subject"),
            "recipient_count": len(contact_names),
            "recipients": contact_names,
        }

    def send(self, campaign_id: int, throttle_rate: float = None) -> dict:
        """Send a campaign to all its recipients.

        Supports throttling to avoid carrier rate limits.
        """
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        if campaign["status"] == "sent":
            return {"error": f"Campaign '{campaign['name']}' already sent"}

        if campaign["status"] == "cancelled":
            return {"error": f"Campaign '{campaign['name']}' was cancelled"}

        # Mark as sending
        self.db.update_campaign(campaign_id, status="sending")

        recipients = self.db.get_campaign_recipients(campaign_id)
        rate = throttle_rate or self.THROTTLE_RATE
        sent = 0
        failed = 0
        results = []

        for recipient in recipients:
            if recipient["status"] in ("sent", "delivered"):
                continue  # skip already-sent (resume support)

            contact = self.db.get_contact(contact_id=recipient["contact_id"])
            if not contact:
                self.db.update_campaign_recipient(
                    recipient["id"], status="skipped", error="Contact not found"
                )
                continue

            # Personalize message
            message = self._personalize(campaign["body"], contact)

            # Determine destination
            to = contact.get("phone") or contact.get("email") or ""
            if not to:
                self.db.update_campaign_recipient(
                    recipient["id"], status="skipped", error="No contact address"
                )
                continue

            # Send via router
            result = self.router.route(
                to, message,
                channel=campaign["channel"] if campaign["channel"] != "auto" else None,
                subject=campaign.get("subject"),
                contact_id=contact["id"],
                priority=self.router.PRIORITY_HIGH,  # campaigns send immediately
            )

            if result.get("error"):
                self.db.update_campaign_recipient(
                    recipient["id"], status="failed", error=result["error"]
                )
                failed += 1
            else:
                msg_id = result.get("message_id")
                self.db.update_campaign_recipient(
                    recipient["id"], status="sent", message_id=msg_id
                )
                sent += 1

            results.append({"contact": contact["name"], **result})

            # Throttle
            if rate > 0 and sent + failed < len(recipients):
                time.sleep(1.0 / rate)

        # Mark campaign complete
        self.db.update_campaign(
            campaign_id, status="sent",
            sent_at=datetime.now(timezone.utc),
            total_sent=sent, total_failed=failed,
        )

        log.info(f"Campaign '{campaign['name']}' sent: {sent} ok, {failed} failed")
        return {
            "campaign": campaign["name"],
            "status": "sent",
            "total_recipients": len(recipients),
            "sent": sent,
            "failed": failed,
            "results": results,
        }

    def cancel(self, campaign_id: int) -> dict:
        """Cancel a draft or scheduled campaign."""
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}
        if campaign["status"] == "sent":
            return {"error": "Cannot cancel an already-sent campaign"}

        self.db.update_campaign(campaign_id, status="cancelled")
        return {"campaign": campaign["name"], "status": "cancelled"}

    def duplicate(self, campaign_id: int, new_name: str = None) -> dict:
        """Duplicate a campaign as a new draft."""
        campaign = self.db.get_campaign(campaign_id)
        if not campaign:
            return {"error": f"Campaign {campaign_id} not found"}

        name = new_name or f"{campaign['name']} (copy)"
        return self.create(
            name=name, body=campaign["body"],
            target_type=campaign["target_type"],
            target_value=campaign["target_value"],
            channel=campaign["channel"],
            subject=campaign.get("subject"),
            template_id=campaign.get("template_id"),
        )

    def _resolve_recipients(self, target_type: str, target_value: str = None) -> list:
        """Resolve target to a list of contacts."""
        if target_type == "single":
            contact = self.contacts.find(target_value)
            return [contact] if contact else []
        elif target_type == "group":
            return self.contacts.list_all(group=target_value)
        elif target_type == "tag":
            return self.contacts.list_all(tag=target_value)
        elif target_type == "all":
            return self.contacts.list_all()
        return []

    def _personalize(self, body: str, contact: dict) -> str:
        """Replace template variables in message body."""
        replacements = {
            "{name}": contact.get("name", ""),
            "{first_name}": contact.get("name", "").split()[0] if contact.get("name") else "",
            "{phone}": contact.get("phone", ""),
            "{email}": contact.get("email", ""),
        }
        result = body
        for token, value in replacements.items():
            result = result.replace(token, value)
        return result
