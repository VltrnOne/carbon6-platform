"""Communications database layer - PostgreSQL with SQLAlchemy."""
import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime,
    Boolean, ForeignKey, Index, Enum as SQLEnum, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from sqlalchemy.sql import func

from ..config.settings import load_config

Base = declarative_base()


class Contact(Base):
    __tablename__ = "comms_contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), index=True)
    email = Column(String(255), index=True)
    preferred_channel = Column(String(20), default="sms")  # sms, email, voice
    tags = Column(JSON, default=list)
    groups = Column(JSON, default=list)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="contact")

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "phone": self.phone,
            "email": self.email, "preferred_channel": self.preferred_channel,
            "tags": self.tags, "groups": self.groups, "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Message(Base):
    __tablename__ = "comms_messages"

    id = Column(Integer, primary_key=True)
    channel = Column(String(20), nullable=False, index=True)  # sms, email, voice
    direction = Column(String(10), nullable=False, index=True)  # inbound, outbound
    contact_id = Column(Integer, ForeignKey("comms_contacts.id"), index=True)
    from_addr = Column(String(255))
    to_addr = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    html_body = Column(Text)
    status = Column(String(20), default="pending", index=True)  # pending, sent, delivered, failed, received
    provider_sid = Column(String(100), index=True)  # Twilio SID / SendGrid ID
    extra_data = Column("metadata", JSON, default=dict)  # provider-specific data
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    contact = relationship("Contact", back_populates="messages")

    __table_args__ = (
        Index("ix_comms_messages_search", "channel", "direction", "created_at"),
        Index("ix_comms_messages_contact_date", "contact_id", "created_at"),
    )

    def to_dict(self):
        return {
            "id": self.id, "channel": self.channel, "direction": self.direction,
            "contact_id": self.contact_id, "from": self.from_addr, "to": self.to_addr,
            "subject": self.subject, "body": self.body, "status": self.status,
            "provider_sid": self.provider_sid, "is_read": self.is_read,
            "metadata": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "contact_name": self.contact.name if self.contact else None,
        }


class ScheduledMessage(Base):
    __tablename__ = "comms_scheduled"

    id = Column(Integer, primary_key=True)
    channel = Column(String(20), nullable=False)
    contact_id = Column(Integer, ForeignKey("comms_contacts.id"))
    to_addr = Column(String(255))
    subject = Column(String(500))
    body = Column(Text)
    send_at = Column(DateTime, nullable=False, index=True)
    recurring_cron = Column(String(100))  # cron expression for recurring
    status = Column(String(20), default="pending")  # pending, sent, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contact = relationship("Contact")


class Template(Base):
    __tablename__ = "comms_templates"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    channel = Column(String(20), nullable=False)  # sms, email, voice
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    variables = Column(JSON, default=list)  # list of variable names
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "channel": self.channel,
            "subject": self.subject, "body": self.body, "variables": self.variables,
        }


class Campaign(Base):
    __tablename__ = "comms_campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    body = Column(Text, nullable=False)
    channel = Column(String(20), default="sms")  # sms, email, voice, auto
    subject = Column(String(500))  # for email campaigns
    template_id = Column(Integer, ForeignKey("comms_templates.id"), nullable=True)
    target_type = Column(String(20), nullable=False)  # single, group, tag, all
    target_value = Column(String(255))  # contact name/id, group name, tag name, or null for all
    status = Column(String(20), default="draft", index=True)  # draft, scheduled, sending, sent, cancelled
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    total_recipients = Column(Integer, default=0)
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    metadata_ = Column("campaign_metadata", JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    template = relationship("Template", foreign_keys=[template_id])

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "body": self.body,
            "channel": self.channel, "subject": self.subject,
            "template_id": self.template_id,
            "target_type": self.target_type, "target_value": self.target_value,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "total_recipients": self.total_recipients,
            "total_sent": self.total_sent,
            "total_delivered": self.total_delivered,
            "total_failed": self.total_failed,
            "metadata": self.metadata_,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CampaignRecipient(Base):
    __tablename__ = "comms_campaign_recipients"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("comms_campaigns.id"), nullable=False, index=True)
    contact_id = Column(Integer, ForeignKey("comms_contacts.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, delivered, failed, skipped
    message_id = Column(Integer, ForeignKey("comms_messages.id"), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

    campaign = relationship("Campaign", backref="recipients")
    contact = relationship("Contact")
    message = relationship("Message")

    __table_args__ = (
        Index("ix_campaign_recipients_lookup", "campaign_id", "contact_id"),
    )

    def to_dict(self):
        return {
            "id": self.id, "campaign_id": self.campaign_id,
            "contact_id": self.contact_id, "status": self.status,
            "message_id": self.message_id,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error": self.error,
            "contact_name": self.contact.name if self.contact else None,
        }


class CommsDB:
    """Communications database manager."""

    def __init__(self):
        config = load_config()
        self.engine = create_engine(config.database.url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    # --- Contact operations ---

    def add_contact(self, name: str, phone: str = None, email: str = None,
                    preferred_channel: str = "sms", tags: list = None,
                    groups: list = None) -> dict:
        with self.get_session() as session:
            contact = Contact(
                name=name, phone=phone, email=email,
                preferred_channel=preferred_channel,
                tags=tags or [], groups=groups or [],
            )
            session.add(contact)
            session.commit()
            session.refresh(contact)
            return contact.to_dict()

    def get_contact(self, contact_id: int = None, name: str = None,
                    phone: str = None, email: str = None) -> Optional[dict]:
        with self.get_session() as session:
            q = session.query(Contact)
            if contact_id:
                q = q.filter(Contact.id == contact_id)
            elif name:
                q = q.filter(Contact.name.ilike(f"%{name}%"))
            elif phone:
                q = q.filter(Contact.phone == phone)
            elif email:
                q = q.filter(Contact.email.ilike(f"%{email}%"))
            contact = q.first()
            return contact.to_dict() if contact else None

    def list_contacts(self, group: str = None, tag: str = None) -> list:
        with self.get_session() as session:
            q = session.query(Contact)
            contacts = q.order_by(Contact.name).all()
            results = [c.to_dict() for c in contacts]
            if group:
                results = [c for c in results if group in (c.get("groups") or [])]
            if tag:
                results = [c for c in results if tag in (c.get("tags") or [])]
            return results

    def resolve_contact(self, identifier: str) -> Optional[dict]:
        """Resolve a contact by name, phone, email, or ID."""
        if identifier.isdigit():
            return self.get_contact(contact_id=int(identifier))
        if "@" in identifier:
            return self.get_contact(email=identifier)
        if identifier.startswith("+") or identifier.replace("-", "").isdigit():
            return self.get_contact(phone=identifier)
        return self.get_contact(name=identifier)

    # --- Message operations ---

    def store_message(self, channel: str, direction: str, from_addr: str,
                      to_addr: str, body: str, subject: str = None,
                      contact_id: int = None, status: str = "pending",
                      provider_sid: str = None, metadata: dict = None) -> dict:
        with self.get_session() as session:
            msg = Message(
                channel=channel, direction=direction, from_addr=from_addr,
                to_addr=to_addr, body=body, subject=subject,
                contact_id=contact_id, status=status,
                provider_sid=provider_sid, extra_data=metadata or {},
                is_read=(direction == "outbound"),
            )
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg.to_dict()

    def update_message_status(self, message_id: int = None,
                               provider_sid: str = None,
                               status: str = "delivered") -> bool:
        with self.get_session() as session:
            q = session.query(Message)
            if message_id:
                q = q.filter(Message.id == message_id)
            elif provider_sid:
                q = q.filter(Message.provider_sid == provider_sid)
            msg = q.first()
            if msg:
                msg.status = status
                session.commit()
                return True
            return False

    def get_inbox(self, channel: str = None, unread_only: bool = False,
                  limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(Message).filter(Message.direction == "inbound")
            if channel:
                q = q.filter(Message.channel == channel)
            if unread_only:
                q = q.filter(Message.is_read == False)
            messages = q.order_by(Message.created_at.desc()).limit(limit).all()
            return [m.to_dict() for m in messages]

    def get_conversation(self, contact_id: int, limit: int = 50) -> list:
        with self.get_session() as session:
            messages = (
                session.query(Message)
                .filter(Message.contact_id == contact_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
                .all()
            )
            return [m.to_dict() for m in messages]

    def search_messages(self, query: str, channel: str = None,
                        contact_id: int = None, limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(Message)
            q = q.filter(
                (Message.body.ilike(f"%{query}%")) |
                (Message.subject.ilike(f"%{query}%"))
            )
            if channel:
                q = q.filter(Message.channel == channel)
            if contact_id:
                q = q.filter(Message.contact_id == contact_id)
            messages = q.order_by(Message.created_at.desc()).limit(limit).all()
            return [m.to_dict() for m in messages]

    def mark_read(self, message_id: int) -> bool:
        with self.get_session() as session:
            msg = session.query(Message).filter(Message.id == message_id).first()
            if msg:
                msg.is_read = True
                session.commit()
                return True
            return False

    # --- Template operations ---

    def save_template(self, name: str, channel: str, body: str,
                      subject: str = None, variables: list = None) -> dict:
        with self.get_session() as session:
            existing = session.query(Template).filter(Template.name == name).first()
            if existing:
                existing.channel = channel
                existing.body = body
                existing.subject = subject
                existing.variables = variables or []
                session.commit()
                session.refresh(existing)
                return existing.to_dict()
            tmpl = Template(
                name=name, channel=channel, body=body,
                subject=subject, variables=variables or [],
            )
            session.add(tmpl)
            session.commit()
            session.refresh(tmpl)
            return tmpl.to_dict()

    def get_template(self, name: str) -> Optional[dict]:
        with self.get_session() as session:
            tmpl = session.query(Template).filter(Template.name == name).first()
            return tmpl.to_dict() if tmpl else None

    def list_templates(self, channel: str = None) -> list:
        with self.get_session() as session:
            q = session.query(Template)
            if channel:
                q = q.filter(Template.channel == channel)
            return [t.to_dict() for t in q.all()]

    # --- Scheduled message operations ---

    def schedule_message(self, channel: str, to_addr: str, body: str,
                          send_at: datetime, subject: str = None,
                          contact_id: int = None,
                          recurring_cron: str = None) -> dict:
        with self.get_session() as session:
            sched = ScheduledMessage(
                channel=channel, to_addr=to_addr, body=body,
                send_at=send_at, subject=subject,
                contact_id=contact_id,
                recurring_cron=recurring_cron,
            )
            session.add(sched)
            session.commit()
            session.refresh(sched)
            return {"id": sched.id, "send_at": sched.send_at.isoformat(), "status": sched.status}

    def get_pending_scheduled(self) -> list:
        with self.get_session() as session:
            now = datetime.now(timezone.utc)
            messages = (
                session.query(ScheduledMessage)
                .filter(ScheduledMessage.status == "pending")
                .filter(ScheduledMessage.send_at <= now)
                .all()
            )
            return [
                {"id": m.id, "channel": m.channel, "to_addr": m.to_addr,
                 "body": m.body, "subject": m.subject, "contact_id": m.contact_id}
                for m in messages
            ]

    # --- Analytics ---

    def get_message_stats(self, days: int = 30) -> dict:
        with self.get_session() as session:
            from sqlalchemy import func as sqlfunc
            cutoff = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0
            )
            base = session.query(Message).filter(
                Message.created_at >= cutoff.__class__(
                    cutoff.year, cutoff.month, cutoff.day - min(days, cutoff.day),
                    tzinfo=timezone.utc
                ) if days < cutoff.day else Message.created_at.isnot(None)
            )

            total = base.count()
            by_channel = {}
            for channel in ["sms", "email", "voice"]:
                by_channel[channel] = {
                    "sent": base.filter(Message.channel == channel, Message.direction == "outbound").count(),
                    "received": base.filter(Message.channel == channel, Message.direction == "inbound").count(),
                }
            by_status = {}
            for status in ["pending", "sent", "delivered", "failed", "received"]:
                by_status[status] = base.filter(Message.status == status).count()

            return {
                "total_messages": total,
                "by_channel": by_channel,
                "by_status": by_status,
                "total_contacts": session.query(Contact).count(),
                "total_templates": session.query(Template).count(),
            }

    # --- Campaign operations ---

    def create_campaign(self, name: str, body: str, target_type: str,
                        target_value: str = None, channel: str = "sms",
                        subject: str = None, template_id: int = None,
                        scheduled_at: datetime = None) -> dict:
        with self.get_session() as session:
            campaign = Campaign(
                name=name, body=body, channel=channel, subject=subject,
                template_id=template_id, target_type=target_type,
                target_value=target_value,
                status="scheduled" if scheduled_at else "draft",
                scheduled_at=scheduled_at,
            )
            session.add(campaign)
            session.commit()
            session.refresh(campaign)
            return campaign.to_dict()

    def get_campaign(self, campaign_id: int) -> Optional[dict]:
        with self.get_session() as session:
            c = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            return c.to_dict() if c else None

    def list_campaigns(self, status: str = None, limit: int = 50) -> list:
        with self.get_session() as session:
            q = session.query(Campaign)
            if status:
                q = q.filter(Campaign.status == status)
            campaigns = q.order_by(Campaign.created_at.desc()).limit(limit).all()
            return [c.to_dict() for c in campaigns]

    def update_campaign(self, campaign_id: int, **kwargs) -> Optional[dict]:
        with self.get_session() as session:
            c = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not c:
                return None
            for key, val in kwargs.items():
                if hasattr(c, key):
                    setattr(c, key, val)
            session.commit()
            session.refresh(c)
            return c.to_dict()

    def delete_campaign(self, campaign_id: int) -> bool:
        with self.get_session() as session:
            c = session.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not c or c.status == "sent":
                return False
            session.query(CampaignRecipient).filter(
                CampaignRecipient.campaign_id == campaign_id
            ).delete()
            session.delete(c)
            session.commit()
            return True

    def add_campaign_recipient(self, campaign_id: int, contact_id: int) -> dict:
        with self.get_session() as session:
            r = CampaignRecipient(campaign_id=campaign_id, contact_id=contact_id)
            session.add(r)
            session.commit()
            session.refresh(r)
            return r.to_dict()

    def update_campaign_recipient(self, recipient_id: int, status: str,
                                   message_id: int = None, error: str = None) -> bool:
        with self.get_session() as session:
            r = session.query(CampaignRecipient).filter(
                CampaignRecipient.id == recipient_id
            ).first()
            if r:
                r.status = status
                r.sent_at = datetime.now(timezone.utc) if status == "sent" else r.sent_at
                if message_id:
                    r.message_id = message_id
                if error:
                    r.error = error
                session.commit()
                return True
            return False

    def get_campaign_recipients(self, campaign_id: int) -> list:
        with self.get_session() as session:
            recipients = (
                session.query(CampaignRecipient)
                .filter(CampaignRecipient.campaign_id == campaign_id)
                .all()
            )
            return [r.to_dict() for r in recipients]
