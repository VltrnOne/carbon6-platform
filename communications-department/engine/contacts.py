"""Contact Manager - CRUD operations for the contact database."""
import csv
import io
import logging
from typing import Optional

log = logging.getLogger("hermes.contacts")


class ContactManager:
    """Manages the contact database."""

    def __init__(self, db):
        self.db = db

    def add(self, name: str, phone: str = None, email: str = None,
            preferred_channel: str = "sms", tags: list = None,
            groups: list = None) -> dict:
        """Add a new contact."""
        # Check for duplicates
        if phone:
            existing = self.db.get_contact(phone=phone)
            if existing:
                return {"error": f"Contact with phone {phone} already exists: {existing['name']}"}
        if email:
            existing = self.db.get_contact(email=email)
            if existing:
                return {"error": f"Contact with email {email} already exists: {existing['name']}"}

        return self.db.add_contact(
            name=name, phone=phone, email=email,
            preferred_channel=preferred_channel,
            tags=tags or [], groups=groups or [],
        )

    def find(self, identifier: str) -> Optional[dict]:
        """Find a contact by name, phone, email, or ID."""
        return self.db.resolve_contact(identifier)

    def list_all(self, group: str = None, tag: str = None) -> list:
        """List all contacts, optionally filtered."""
        return self.db.list_contacts(group=group, tag=tag)

    def get_conversation(self, identifier: str, limit: int = 50) -> dict:
        """Get full conversation history with a contact."""
        contact = self.db.resolve_contact(identifier)
        if not contact:
            return {"error": f"Contact not found: {identifier}"}
        messages = self.db.get_conversation(contact["id"], limit=limit)
        return {"contact": contact, "messages": messages}

    def import_csv(self, csv_content: str) -> dict:
        """Import contacts from CSV string (name,phone,email,groups)."""
        reader = csv.DictReader(io.StringIO(csv_content))
        imported = 0
        errors = []
        for row in reader:
            try:
                name = row.get("name", "").strip()
                if not name:
                    continue
                groups = [g.strip() for g in row.get("groups", "").split(";") if g.strip()]
                self.db.add_contact(
                    name=name,
                    phone=row.get("phone", "").strip() or None,
                    email=row.get("email", "").strip() or None,
                    groups=groups,
                )
                imported += 1
            except Exception as e:
                errors.append(f"{row.get('name', '?')}: {e}")
        return {"imported": imported, "errors": errors}

    def export_csv(self) -> str:
        """Export all contacts as CSV."""
        contacts = self.db.list_contacts()
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["name", "phone", "email", "preferred_channel", "tags", "groups"])
        writer.writeheader()
        for c in contacts:
            writer.writerow({
                "name": c["name"], "phone": c.get("phone", ""),
                "email": c.get("email", ""),
                "preferred_channel": c.get("preferred_channel", "sms"),
                "tags": ";".join(c.get("tags", [])),
                "groups": ";".join(c.get("groups", [])),
            })
        return output.getvalue()
