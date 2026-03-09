"""Email Account Bridge - Connect to your personal email accounts on your phone.

Supports multiple email accounts (Gmail, iCloud, Outlook, etc.)
All emails are accessed server-side via IMAP/SMTP - no phone bridge needed.
Your phone and this system see the same mailbox.
"""
import json
import logging
import os
from typing import Optional

from ..config.settings import load_config

log = logging.getLogger("hermes.email_bridge")


class EmailAccountBridge:
    """Manage multiple email accounts that mirror what's on your phone.

    Since email uses IMAP/SMTP, we connect to the same mail server
    your phone connects to. No bridge app needed - same mailbox, same messages.
    """

    def __init__(self, db=None):
        self.db = db
        self.config = load_config().email
        self.accounts = self._load_accounts()

    def _load_accounts(self) -> list:
        """Load configured email accounts."""
        accounts = []

        # Primary account from env
        if self.config.smtp_user:
            accounts.append({
                "name": "primary",
                "email": self.config.smtp_user,
                "smtp_host": self.config.smtp_host,
                "smtp_port": self.config.smtp_port,
                "imap_host": self.config.imap_host,
                "imap_port": self.config.imap_port,
                "username": self.config.smtp_user,
                "configured": self.config.smtp_configured,
            })

        # Additional accounts from JSON env var
        try:
            additional = json.loads(self.config.additional_accounts)
            for acct in additional:
                accounts.append({
                    "name": acct.get("name", acct.get("email", "unknown")),
                    "email": acct.get("email", ""),
                    "smtp_host": acct.get("smtp_host", "smtp.gmail.com"),
                    "smtp_port": acct.get("smtp_port", 587),
                    "imap_host": acct.get("imap_host", "imap.gmail.com"),
                    "imap_port": acct.get("imap_port", 993),
                    "username": acct.get("username", acct.get("email", "")),
                    "configured": bool(acct.get("email") and acct.get("password")),
                })
        except (json.JSONDecodeError, TypeError):
            pass

        return accounts

    def list_accounts(self) -> list:
        """List configured email accounts."""
        return [
            {"name": a["name"], "email": a["email"], "configured": a["configured"]}
            for a in self.accounts
        ]

    def get_account(self, name: str = None, email: str = None) -> Optional[dict]:
        """Get a specific email account config."""
        for acct in self.accounts:
            if name and acct["name"] == name:
                return acct
            if email and acct["email"] == email:
                return acct
        return None

    def status(self) -> dict:
        """Status of all email accounts."""
        return {
            "total_accounts": len(self.accounts),
            "configured": len([a for a in self.accounts if a["configured"]]),
            "accounts": self.list_accounts(),
            "note": "Email connects to the same IMAP/SMTP servers as your phone - same mailbox, no bridge needed.",
        }


# Common email provider configs for easy setup
EMAIL_PROVIDERS = {
    "gmail": {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
        "note": "Use App Password (not regular password). Enable at myaccount.google.com/apppasswords",
    },
    "icloud": {
        "smtp_host": "smtp.mail.me.com",
        "smtp_port": 587,
        "imap_host": "imap.mail.me.com",
        "imap_port": 993,
        "note": "Use App-Specific Password from appleid.apple.com",
    },
    "outlook": {
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "note": "Use your regular password or app password if 2FA enabled",
    },
    "yahoo": {
        "smtp_host": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "imap_host": "imap.mail.yahoo.com",
        "imap_port": 993,
        "note": "Generate app password at login.yahoo.com/account/security",
    },
}
