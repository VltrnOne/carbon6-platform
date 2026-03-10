#!/usr/bin/env python3
"""HERMES - Communications Director CLI.

The main command interface for the Communications Department.
Parses natural language and slash commands to route to sub-agents.

Usage:
    hermes text <contact> <message>
    hermes email <contact> <subject> -- <body>
    hermes call <contact> [message]
    hermes search <query>
    hermes inbox [--channel sms|email|voice] [--unread]
    hermes contacts [list|add|find|import|export]
    hermes broadcast <group> <message>
    hermes schedule <datetime> <channel> <to> <message>
    hermes templates [list|create|use]
    hermes analytics [--days N]
    hermes campaign [create|read|list|send|preview|cancel|duplicate]
    hermes voice [listen|file <path>|status]
    hermes status
    hermes setup
"""
import argparse
import json
import sys
import os
from datetime import datetime, timezone

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communications_department.engine.database import CommsDB
from communications_department.engine.sms import SMSEngine
from communications_department.engine.email_engine import EmailEngine
from communications_department.engine.voice import VoiceEngine
from communications_department.engine.contacts import ContactManager
from communications_department.engine.search import SearchEngine
from communications_department.engine.router import MessageRouter
from communications_department.engine.scheduler import MessageScheduler
from communications_department.engine.inbox import UnifiedInbox
from communications_department.engine.analytics import AnalyticsEngine
from communications_department.engine.imessage import IMessageEngine
from communications_department.engine.email_bridge import EmailAccountBridge, EMAIL_PROVIDERS
from communications_department.engine.campaign import CampaignEngine
from communications_department.engine.voice_command import VoiceCommander
from communications_department.config.settings import load_config


class Hermes:
    """HERMES - Communications Director."""

    def __init__(self):
        self.config = load_config()
        self.db = CommsDB()
        self.sms = SMSEngine(db=self.db)
        self.email = EmailEngine(db=self.db)
        self.voice = VoiceEngine(db=self.db)
        self.imessage = IMessageEngine(db=self.db)
        self.email_bridge = EmailAccountBridge(db=self.db)
        self.contacts = ContactManager(db=self.db)
        self.search = SearchEngine(db=self.db, email_engine=self.email)
        self.router = MessageRouter(
            db=self.db, sms_engine=self.sms,
            email_engine=self.email, voice_engine=self.voice,
            imessage_engine=self.imessage,
        )
        self.scheduler = MessageScheduler(db=self.db, router=self.router)
        self.inbox = UnifiedInbox(db=self.db, email_engine=self.email)
        self.analytics = AnalyticsEngine(db=self.db)
        self.campaigns = CampaignEngine(db=self.db, contacts=self.contacts, router=self.router)
        self.voice_cmd = VoiceCommander(hermes=self)

    def init(self):
        """Initialize database tables."""
        self.db.init_tables()
        print("[HERMES] Database initialized.")

    def handle_command(self, args: list) -> dict:
        """Parse and execute a command."""
        if not args:
            return self.status()

        cmd = args[0].lower()
        rest = args[1:]

        handlers = {
            "text": self._cmd_text,
            "sms": self._cmd_sms_only,
            "itext": self._cmd_text,
            "imessage": self._cmd_text,
            "email": self._cmd_email,
            "mail": self._cmd_email,
            "call": self._cmd_call,
            "voice": self._cmd_call,
            "search": self._cmd_search,
            "find": self._cmd_search,
            "inbox": self._cmd_inbox,
            "contacts": self._cmd_contacts,
            "contact": self._cmd_contacts,
            "broadcast": self._cmd_broadcast,
            "schedule": self._cmd_schedule,
            "templates": self._cmd_templates,
            "template": self._cmd_templates,
            "analytics": self._cmd_analytics,
            "stats": self._cmd_analytics,
            "status": lambda _: self.status(),
            "setup": lambda _: self.setup_check(),
            "setup-imessage": lambda _: self.setup_imessage(),
            "setup-email": lambda _: self.setup_email_accounts(),
            "init": lambda _: self.init() or {"status": "initialized"},
            "send": self._cmd_send,
            "campaign": self._cmd_campaign,
            "campaigns": self._cmd_campaign,
            "voice": self._cmd_voice,
            "listen": lambda _: self.voice_cmd.listen(),
            "accounts": lambda _: self.email_bridge.status(),
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(rest)

        # Try natural language parsing
        return self._parse_natural(args)

    def _cmd_text(self, args: list) -> dict:
        """Send text: prefers iMessage bridge (your phone), falls back to Twilio SMS."""
        if len(args) < 2:
            return {"error": "Usage: hermes text <contact> <message>"}
        contact_id_str = args[0]
        message = " ".join(args[1:])

        contact = self.contacts.find(contact_id_str)
        phone = None
        contact_id = None
        if contact and contact.get("phone"):
            phone = contact["phone"]
            contact_id = contact["id"]
        elif contact_id_str.startswith("+") or contact_id_str.replace("-", "").isdigit():
            phone = contact_id_str
        else:
            return {"error": f"Contact '{contact_id_str}' not found or has no phone number"}

        # Prefer iMessage bridge (sends from your actual phone number)
        if self.imessage.is_configured:
            return self.imessage.send(phone, message, contact_id=contact_id)

        # Fallback to Twilio SMS
        if self.sms.is_configured:
            return self.sms.send(phone, message, contact_id=contact_id)

        return {"error": "No text channel configured. Run: hermes setup-imessage (or set Twilio env vars)"}

    def _cmd_sms_only(self, args: list) -> dict:
        """Force send via Twilio SMS (bypass iMessage bridge)."""
        if len(args) < 2:
            return {"error": "Usage: hermes sms <contact> <message>"}
        contact_id_str = args[0]
        message = " ".join(args[1:])

        contact = self.contacts.find(contact_id_str)
        if contact and contact.get("phone"):
            return self.sms.send(contact["phone"], message, contact_id=contact["id"])
        elif contact_id_str.startswith("+") or contact_id_str.replace("-", "").isdigit():
            return self.sms.send(contact_id_str, message)
        return {"error": f"Contact '{contact_id_str}' not found or has no phone number"}

    def _cmd_email(self, args: list) -> dict:
        """Send email: email <contact> <subject> -- <body>"""
        if len(args) < 2:
            return {"error": "Usage: hermes email <contact> <subject> -- <body>"}

        contact_id_str = args[0]
        # Find -- separator
        if "--" in args:
            sep_idx = args.index("--")
            subject = " ".join(args[1:sep_idx])
            body = " ".join(args[sep_idx + 1:])
        else:
            subject = args[1]
            body = " ".join(args[2:]) if len(args) > 2 else ""

        contact = self.contacts.find(contact_id_str)
        if contact and contact.get("email"):
            return self.email.send(contact["email"], subject, body, contact_id=contact["id"])
        elif "@" in contact_id_str:
            return self.email.send(contact_id_str, subject, body)
        return {"error": f"Contact '{contact_id_str}' not found or has no email"}

    def _cmd_call(self, args: list) -> dict:
        """Call: call <contact> [message]"""
        if not args:
            return {"error": "Usage: hermes call <contact> [message]"}
        contact_id_str = args[0]
        message = " ".join(args[1:]) if len(args) > 1 else None

        contact = self.contacts.find(contact_id_str)
        if contact and contact.get("phone"):
            return self.voice.call(contact["phone"], message=message, contact_id=contact["id"])
        elif contact_id_str.startswith("+") or contact_id_str.replace("-", "").isdigit():
            return self.voice.call(contact_id_str, message=message)
        return {"error": f"Contact '{contact_id_str}' not found or has no phone number"}

    def _cmd_search(self, args: list) -> dict:
        """Search: search <query> [--channel sms|email] [--contact name]"""
        if not args:
            return {"error": "Usage: hermes search <query>"}

        channel = None
        contact = None
        query_parts = []

        i = 0
        while i < len(args):
            if args[i] == "--channel" and i + 1 < len(args):
                channel = args[i + 1]
                i += 2
            elif args[i] == "--contact" and i + 1 < len(args):
                contact = args[i + 1]
                i += 2
            else:
                query_parts.append(args[i])
                i += 1

        query = " ".join(query_parts)
        return self.search.search(query, channel=channel, contact=contact)

    def _cmd_inbox(self, args: list) -> dict:
        """Inbox: inbox [--channel sms|email] [--unread] [--sync]"""
        channel = None
        unread = False
        sync = False

        i = 0
        while i < len(args):
            if args[i] == "--channel" and i + 1 < len(args):
                channel = args[i + 1]
                i += 2
            elif args[i] == "--unread":
                unread = True
                i += 1
            elif args[i] == "--sync":
                sync = True
                i += 1
            else:
                i += 1

        if sync:
            self.inbox.sync_email()

        return self.inbox.get(channel=channel, unread_only=unread)

    def _cmd_contacts(self, args: list) -> dict:
        """Contacts: contacts [list|add|find|import|export]"""
        if not args:
            return {"contacts": self.contacts.list_all()}

        action = args[0].lower()
        if action == "list":
            group = None
            tag = None
            if "--group" in args:
                idx = args.index("--group")
                group = args[idx + 1] if idx + 1 < len(args) else None
            if "--tag" in args:
                idx = args.index("--tag")
                tag = args[idx + 1] if idx + 1 < len(args) else None
            return {"contacts": self.contacts.list_all(group=group, tag=tag)}

        elif action == "add" and len(args) >= 2:
            name = args[1]
            phone = None
            email_addr = None
            for a in args[2:]:
                if a.startswith("+") or a.replace("-", "").isdigit():
                    phone = a
                elif "@" in a:
                    email_addr = a
            return self.contacts.add(name, phone=phone, email=email_addr)

        elif action == "find" and len(args) >= 2:
            return self.contacts.find(args[1]) or {"error": "Not found"}

        elif action == "conversation" and len(args) >= 2:
            return self.contacts.get_conversation(args[1])

        elif action == "export":
            csv_data = self.contacts.export_csv()
            return {"csv": csv_data}

        return {"error": f"Unknown contacts action: {action}"}

    def _cmd_broadcast(self, args: list) -> dict:
        """Broadcast: broadcast <group> <message...>"""
        if len(args) < 2:
            return {"error": "Usage: hermes broadcast <group> <message>"}
        group = args[0]
        message = " ".join(args[1:])
        contacts = self.contacts.list_all(group=group)
        if not contacts:
            return {"error": f"No contacts in group: {group}"}

        results = []
        for contact in contacts:
            result = self.router.route(
                contact.get("phone") or contact.get("email") or "",
                message, contact_id=contact["id"],
            )
            results.append({"contact": contact["name"], **result})
        return {"broadcast_to": group, "sent": len(results), "results": results}

    def _cmd_schedule(self, args: list) -> dict:
        """Schedule: schedule <datetime> <channel> <to> <message...>"""
        if len(args) < 4:
            return {"error": "Usage: hermes schedule <datetime> <channel> <to> <message>"}
        try:
            send_at = datetime.fromisoformat(args[0])
        except ValueError:
            return {"error": f"Invalid datetime: {args[0]}. Use ISO format: 2026-03-10T15:00:00"}
        channel = args[1]
        to = args[2]
        message = " ".join(args[3:])
        return self.scheduler.schedule(channel, to, message, send_at)

    def _cmd_templates(self, args: list) -> dict:
        """Templates: templates [list|create|use]"""
        if not args or args[0] == "list":
            channel = None
            if "--channel" in args:
                idx = args.index("--channel")
                channel = args[idx + 1] if idx + 1 < len(args) else None
            return {"templates": self.db.list_templates(channel=channel)}

        if args[0] == "create" and len(args) >= 4:
            name = args[1]
            channel = args[2]
            body = " ".join(args[3:])
            return self.db.save_template(name=name, channel=channel, body=body)

        if args[0] == "get" and len(args) >= 2:
            return self.db.get_template(args[1]) or {"error": "Template not found"}

        return {"error": "Usage: hermes templates [list|create <name> <channel> <body>|get <name>]"}

    def _cmd_analytics(self, args: list) -> dict:
        """Analytics: analytics [--days N] [--contact name]"""
        days = 30
        contact = None
        i = 0
        while i < len(args):
            if args[i] == "--days" and i + 1 < len(args):
                days = int(args[i + 1])
                i += 2
            elif args[i] == "--contact" and i + 1 < len(args):
                contact = args[i + 1]
                i += 2
            else:
                i += 1

        if contact:
            return self.analytics.contact_engagement(contact)
        return self.analytics.dashboard(days=days)

    def _cmd_campaign(self, args: list) -> dict:
        """Campaign management: campaign [create|read|list|send|preview|cancel|duplicate]

        Examples:
            hermes campaign create "Spring Sale" --body "20% off!" --target group --group vip
            hermes campaign create "Welcome" --body "Hi {first_name}!" --target single --to John
            hermes campaign create "Big Blast" --body "New launch!" --target all
            hermes campaign list [--status draft|sent|cancelled]
            hermes campaign read <id>
            hermes campaign preview <id>
            hermes campaign send <id> [--throttle 2]
            hermes campaign cancel <id>
            hermes campaign duplicate <id> [--name "New Name"]
        """
        if not args:
            return self.campaigns.list()

        action = args[0].lower()

        if action == "list":
            status = None
            if "--status" in args:
                idx = args.index("--status")
                status = args[idx + 1] if idx + 1 < len(args) else None
            return self.campaigns.list(status=status)

        elif action == "create":
            if len(args) < 2:
                return {"error": "Usage: hermes campaign create <name> --body <message> --target <single|group|tag|all> [--group <name>|--to <contact>|--tag <tag>]"}
            name = args[1]
            body = channel = subject = target_type = target_value = None
            scheduled_at = None
            i = 2
            while i < len(args):
                if args[i] == "--body" and i + 1 < len(args):
                    body = args[i + 1]; i += 2
                elif args[i] == "--channel" and i + 1 < len(args):
                    channel = args[i + 1]; i += 2
                elif args[i] == "--subject" and i + 1 < len(args):
                    subject = args[i + 1]; i += 2
                elif args[i] == "--target" and i + 1 < len(args):
                    target_type = args[i + 1]; i += 2
                elif args[i] in ("--group", "--to", "--tag") and i + 1 < len(args):
                    target_value = args[i + 1]
                    if args[i] == "--group":
                        target_type = target_type or "group"
                    elif args[i] == "--tag":
                        target_type = target_type or "tag"
                    elif args[i] == "--to":
                        target_type = target_type or "single"
                    i += 2
                elif args[i] == "--schedule" and i + 1 < len(args):
                    try:
                        scheduled_at = datetime.fromisoformat(args[i + 1])
                    except ValueError:
                        return {"error": f"Invalid datetime: {args[i+1]}"}
                    i += 2
                else:
                    i += 1

            if not body:
                return {"error": "Missing --body. Usage: hermes campaign create <name> --body <message> --target all"}
            target_type = target_type or "all"

            return self.campaigns.create(
                name=name, body=body, target_type=target_type,
                target_value=target_value, channel=channel or "sms",
                subject=subject, scheduled_at=scheduled_at,
            )

        elif action == "read" and len(args) >= 2:
            return self.campaigns.read(int(args[1]))

        elif action == "preview" and len(args) >= 2:
            return self.campaigns.preview(int(args[1]))

        elif action == "send" and len(args) >= 2:
            throttle = None
            if "--throttle" in args:
                idx = args.index("--throttle")
                throttle = float(args[idx + 1]) if idx + 1 < len(args) else None
            return self.campaigns.send(int(args[1]), throttle_rate=throttle)

        elif action == "cancel" and len(args) >= 2:
            return self.campaigns.cancel(int(args[1]))

        elif action == "duplicate" and len(args) >= 2:
            new_name = None
            if "--name" in args:
                idx = args.index("--name")
                new_name = args[idx + 1] if idx + 1 < len(args) else None
            return self.campaigns.duplicate(int(args[1]), new_name=new_name)

        return {"error": "Usage: hermes campaign [create|read|list|send|preview|cancel|duplicate]"}

    def _cmd_voice(self, args: list) -> dict:
        """Voice command: voice [listen|file <path>|status|exec <text>]

        Examples:
            hermes voice listen                     # mic → command
            hermes voice listen --duration 10       # record for 10 seconds
            hermes voice file /path/to/audio.wav    # file → command
            hermes voice exec "send campaign 5"     # text → parsed as voice command
            hermes voice status                     # check STT engine status
        """
        if not args or args[0] == "status":
            return self.voice_cmd.status()

        action = args[0].lower()

        if action == "listen":
            duration = 5
            if "--duration" in args:
                idx = args.index("--duration")
                duration = int(args[idx + 1]) if idx + 1 < len(args) else 5
            print("[HERMES] Listening... speak your command.")
            return self.voice_cmd.listen(duration=duration)

        elif action == "file" and len(args) >= 2:
            return self.voice_cmd.from_file(args[1])

        elif action == "exec" and len(args) >= 2:
            text = " ".join(args[1:])
            return self.voice_cmd.execute(text)

        return {"error": "Usage: hermes voice [listen|file <path>|exec <text>|status]"}

    def _cmd_send(self, args: list) -> dict:
        """Smart send: auto-detect channel. send <contact> <message...>"""
        if len(args) < 2:
            return {"error": "Usage: hermes send <contact> <message>"}
        contact_id_str = args[0]
        message = " ".join(args[1:])

        contact = self.contacts.find(contact_id_str)
        if contact:
            to = contact.get("phone") or contact.get("email") or ""
            return self.router.route(to, message, contact_id=contact["id"])

        # Try direct routing
        return self.router.route(contact_id_str, message)

    def _parse_natural(self, args: list) -> dict:
        """Parse natural language commands."""
        text = " ".join(args).lower()

        if any(w in text for w in ["text ", "sms ", "message "]):
            # Extract after the keyword
            for keyword in ["text ", "sms ", "message "]:
                if keyword in text:
                    rest = text.split(keyword, 1)[1]
                    parts = rest.split(" ", 1)
                    if len(parts) >= 2:
                        return self._cmd_text(parts)

        if any(w in text for w in ["email ", "mail "]):
            for keyword in ["email ", "mail "]:
                if keyword in text:
                    return {"hint": "Use: hermes email <contact> <subject> -- <body>"}

        if any(w in text for w in ["call ", "phone "]):
            for keyword in ["call ", "phone "]:
                if keyword in text:
                    rest = text.split(keyword, 1)[1].strip()
                    if rest:
                        return self._cmd_call([rest])

        if "search" in text or "find" in text:
            for keyword in ["search ", "find "]:
                if keyword in text:
                    query = text.split(keyword, 1)[1]
                    return self._cmd_search([query])

        if "inbox" in text:
            return self._cmd_inbox([])

        # Campaign natural language (delegate to voice commander's parser)
        campaign_result = self.voice_cmd._parse_campaign_command(" ".join(args))
        if campaign_result:
            return campaign_result

        return {"error": f"Unknown command. Try: hermes text/email/call/search/inbox/contacts/campaign/voice/status"}

    def status(self) -> dict:
        """Get system status."""
        return {
            "agent": "HERMES",
            "department": "Communications",
            "channels": {
                "imessage": {"configured": self.imessage.is_configured, "provider": "iPhone (Pushcut + Shortcuts)", "priority": "PRIMARY"},
                "sms": {"configured": self.sms.is_configured, "provider": "Twilio (fallback)"},
                "email_send": {"configured": self.email.can_send, "provider": "SMTP/SendGrid"},
                "email_receive": {"configured": self.email.can_receive, "provider": "IMAP"},
                "voice": {"configured": self.voice.is_configured, "provider": "Twilio"},
            },
            "imessage_queue": self.imessage.queue_size(),
            "message_queue": self.router.queue_size(),
            "email_accounts": self.email_bridge.list_accounts(),
            "voice_command": self.voice_cmd.status(),
            "sub_agents": [
                "HERMES-IMESSAGE", "HERMES-SMS", "HERMES-EMAIL", "HERMES-VOICE",
                "HERMES-SEARCH", "HERMES-ROUTER", "HERMES-TEMPLATE",
                "HERMES-SCHEDULER", "HERMES-INBOX", "HERMES-CONTACTS",
                "HERMES-WEBHOOK", "HERMES-ANALYTICS", "HERMES-BROADCAST",
                "HERMES-CAMPAIGN", "HERMES-VOICE-CMD",
            ],
        }

    def setup_check(self) -> dict:
        """Check what needs to be configured."""
        issues = []
        if not self.imessage.is_configured:
            issues.append("iMessage: Set PUSHCUT_API_KEY and PUSHCUT_DEVICE_NAME (run: hermes setup-imessage)")
        if not self.sms.is_configured:
            issues.append("SMS Fallback: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")
        if not self.email.can_send:
            issues.append("Email Send: Set SMTP_USER, SMTP_PASSWORD (or SENDGRID_API_KEY)")
        if not self.email.can_receive:
            issues.append("Email Receive: Set IMAP_USER, IMAP_PASSWORD")
        if not self.voice.is_configured:
            issues.append("Voice: Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER")

        return {
            "configured": len(issues) == 0,
            "issues": issues if issues else ["All channels configured!"],
            "env_template": {
                "# -- iMessage Bridge (PRIMARY - sends from your phone) --": "",
                "PUSHCUT_API_KEY": "your_pushcut_api_key",
                "PUSHCUT_DEVICE_NAME": "My iPhone",
                "IMESSAGE_SEND_SHORTCUT": "HERMES Send Message",
                "# -- Twilio (FALLBACK for SMS/Voice) --": "",
                "TWILIO_ACCOUNT_SID": "ACxxxxxxxxxx",
                "TWILIO_AUTH_TOKEN": "your_auth_token",
                "TWILIO_PHONE_NUMBER": "+1234567890",
                "# -- Email --": "",
                "SMTP_HOST": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USER": "your@gmail.com",
                "SMTP_PASSWORD": "your_app_password",
                "IMAP_HOST": "imap.gmail.com",
                "IMAP_PORT": "993",
                "IMAP_USER": "your@gmail.com",
                "IMAP_PASSWORD": "your_app_password",
                "SENDGRID_API_KEY": "SG.xxxxxxxxxx",
            },
        }


    def setup_imessage(self) -> dict:
        """Guide for setting up iMessage bridge on iPhone."""
        return {
            "title": "iMessage Bridge Setup (iPhone)",
            "steps": [
                {
                    "step": 1,
                    "action": "Install Pushcut from the App Store",
                    "detail": "Pushcut turns your iPhone into a webhook-triggered automation server.",
                },
                {
                    "step": 2,
                    "action": "Subscribe to Pushcut Automation Server",
                    "detail": "Required for background webhook listening. $2/month or $20/year.",
                },
                {
                    "step": 3,
                    "action": "Get your Pushcut API Key",
                    "detail": "Open Pushcut → Account → API Key. Copy it.",
                },
                {
                    "step": 4,
                    "action": "Create the 'HERMES Send Message' Shortcut on your iPhone",
                    "detail": "Open Shortcuts app → New Shortcut → Add actions:\n"
                              "  1. 'Get Dictionary Value' (key: 'to' from Shortcut Input)\n"
                              "  2. 'Get Dictionary Value' (key: 'body' from Shortcut Input)\n"
                              "  3. 'Send Message' (to: result of #1, body: result of #2)\n"
                              "  Name it: 'HERMES Send Message'",
                },
                {
                    "step": 5,
                    "action": "Create inbound message automation",
                    "detail": "Shortcuts → Automation → When I Receive a Message → Run Immediately\n"
                              "  1. 'Get Details of Messages' (sender, content)\n"
                              "  2. 'Get Contents of URL' → POST to:\n"
                              f"     https://vltrn.cloud:3100/api/comms/imessage/inbound\n"
                              "     Body: {\"from\": sender, \"body\": content}",
                },
                {
                    "step": 6,
                    "action": "Set environment variables on this server",
                    "detail": "Add to /root/carbon6-platform/.env:\n"
                              "  PUSHCUT_API_KEY=your_key_here\n"
                              "  PUSHCUT_DEVICE_NAME=My iPhone",
                },
                {
                    "step": 7,
                    "action": "Test: hermes text 'Test User' 'Hello from HERMES!'",
                    "detail": "This should trigger Pushcut → run Shortcut → send iMessage from your number.",
                },
            ],
            "how_it_works": {
                "outbound": "hermes text → Pushcut webhook → iPhone Shortcut → Messages.app → iMessage/SMS from YOUR number",
                "inbound": "Someone texts you → Shortcuts automation → webhook to HERMES → stored in DB → unified inbox",
                "offline": "If phone is off/asleep, messages queue in Redis and retry when phone reconnects",
                "fallback": "If Pushcut unreachable + Twilio configured, falls back to Twilio SMS",
            },
            "current_status": self.imessage.status(),
        }

    def setup_email_accounts(self) -> dict:
        """Guide for connecting email accounts."""
        return {
            "title": "Email Account Setup",
            "note": "Email works server-side via IMAP/SMTP - same servers your phone uses. No bridge needed.",
            "providers": EMAIL_PROVIDERS,
            "steps": [
                "1. Choose your email provider below",
                "2. Generate an App Password (required for Gmail, iCloud with 2FA)",
                "3. Set the environment variables",
                "4. Run: hermes email <contact> <subject> -- <body>",
            ],
            "env_vars": {
                "gmail": "SMTP_HOST=smtp.gmail.com SMTP_PORT=587 SMTP_USER=you@gmail.com SMTP_PASSWORD=app_password IMAP_HOST=imap.gmail.com IMAP_PORT=993 IMAP_USER=you@gmail.com IMAP_PASSWORD=app_password",
                "icloud": "SMTP_HOST=smtp.mail.me.com SMTP_PORT=587 SMTP_USER=you@icloud.com SMTP_PASSWORD=app_specific_password IMAP_HOST=imap.mail.me.com IMAP_PORT=993 IMAP_USER=you@icloud.com IMAP_PASSWORD=app_specific_password",
            },
            "multiple_accounts": "Set EMAIL_ADDITIONAL_ACCOUNTS as JSON array: [{\"email\": \"x@y.com\", \"password\": \"...\", \"smtp_host\": \"...\"}]",
            "current_status": self.email_bridge.status(),
        }


def main():
    hermes = Hermes()
    if len(sys.argv) < 2:
        result = hermes.status()
    else:
        result = hermes.handle_command(sys.argv[1:])
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
