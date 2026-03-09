"""Email Engine - Send via SMTP/SendGrid, receive via IMAP."""
import email
import imaplib
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional

from ..config.settings import load_config

log = logging.getLogger("hermes.email")


class EmailEngine:
    """Handles email send (SMTP/SendGrid) and receive (IMAP)."""

    def __init__(self, db=None):
        self.config = load_config().email
        self.db = db

    @property
    def can_send(self) -> bool:
        return self.config.smtp_configured or self.config.sendgrid_configured

    @property
    def can_receive(self) -> bool:
        return self.config.imap_configured

    def send(self, to: str, subject: str, body: str, html: str = None,
             attachments: list = None, contact_id: int = None) -> dict:
        """Send email via SMTP or SendGrid."""
        if self.config.sendgrid_configured:
            return self._send_sendgrid(to, subject, body, html, contact_id)
        if self.config.smtp_configured:
            return self._send_smtp(to, subject, body, html, attachments, contact_id)
        return {"error": "Email not configured. Set SMTP_USER/SMTP_PASSWORD or SENDGRID_API_KEY"}

    def _send_smtp(self, to: str, subject: str, body: str, html: str = None,
                   attachments: list = None, contact_id: int = None) -> dict:
        """Send via SMTP."""
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.config.smtp_user
            msg["To"] = to
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            if attachments:
                for filepath in attachments:
                    try:
                        with open(filepath, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                "Content-Disposition",
                                f"attachment; filename={filepath.split('/')[-1]}",
                            )
                            msg.attach(part)
                    except FileNotFoundError:
                        log.warning(f"Attachment not found: {filepath}")

            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls()
                server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)

            result = {
                "status": "sent", "to": to, "subject": subject, "channel": "email",
            }

            if self.db:
                self.db.store_message(
                    channel="email", direction="outbound",
                    from_addr=self.config.smtp_user, to_addr=to,
                    body=body, subject=subject, contact_id=contact_id,
                    status="sent",
                )

            log.info(f"Email sent to {to}: {subject}")
            return result

        except Exception as e:
            log.error(f"SMTP send failed to {to}: {e}")
            if self.db:
                self.db.store_message(
                    channel="email", direction="outbound",
                    from_addr=self.config.smtp_user, to_addr=to,
                    body=body, subject=subject, contact_id=contact_id,
                    status="failed", metadata={"error": str(e)},
                )
            return {"error": str(e)}

    def _send_sendgrid(self, to: str, subject: str, body: str,
                       html: str = None, contact_id: int = None) -> dict:
        """Send via SendGrid API."""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content

            sg = sendgrid.SendGridAPIClient(api_key=self.config.sendgrid_api_key)
            from_email = Email(self.config.smtp_user or "noreply@vltrn.cloud")
            to_email = To(to)
            content = Content("text/html", html) if html else Content("text/plain", body)
            mail = Mail(from_email, to_email, subject, content)

            response = sg.client.mail.send.post(request_body=mail.get())

            result = {
                "status": "sent",
                "status_code": response.status_code,
                "to": to, "subject": subject, "channel": "email",
            }

            if self.db:
                self.db.store_message(
                    channel="email", direction="outbound",
                    from_addr=str(from_email), to_addr=to,
                    body=body, html_body=html, subject=subject,
                    contact_id=contact_id, status="sent",
                )

            log.info(f"SendGrid email sent to {to}: {subject}")
            return result

        except Exception as e:
            log.error(f"SendGrid send failed to {to}: {e}")
            return {"error": str(e)}

    def fetch_inbox(self, folder: str = "INBOX", limit: int = 20,
                    unread_only: bool = False) -> list:
        """Fetch emails from IMAP inbox."""
        if not self.can_receive:
            return [{"error": "IMAP not configured. Set IMAP_USER/IMAP_PASSWORD"}]

        try:
            imap = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
            imap.login(self.config.imap_user, self.config.imap_password)
            imap.select(folder)

            search_criteria = "UNSEEN" if unread_only else "ALL"
            _, message_numbers = imap.search(None, search_criteria)

            nums = message_numbers[0].split()
            # Get most recent
            nums = nums[-limit:] if len(nums) > limit else nums

            emails = []
            for num in reversed(nums):
                _, msg_data = imap.fetch(num, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                body_text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body_text = part.get_payload(decode=True).decode("utf-8", errors="replace")
                            break
                else:
                    body_text = msg.get_payload(decode=True).decode("utf-8", errors="replace")

                emails.append({
                    "id": num.decode(),
                    "from": msg.get("From", ""),
                    "to": msg.get("To", ""),
                    "subject": msg.get("Subject", ""),
                    "date": msg.get("Date", ""),
                    "body": body_text[:500],
                    "channel": "email",
                })

                # Store inbound in DB
                if self.db:
                    from_addr = msg.get("From", "")
                    contact = self.db.get_contact(email=from_addr) if self.db else None
                    self.db.store_message(
                        channel="email", direction="inbound",
                        from_addr=from_addr,
                        to_addr=msg.get("To", ""),
                        body=body_text[:2000],
                        subject=msg.get("Subject", ""),
                        contact_id=contact["id"] if contact else None,
                        status="received",
                    )

            imap.logout()
            return emails

        except Exception as e:
            log.error(f"IMAP fetch failed: {e}")
            return [{"error": str(e)}]

    def search_emails(self, query: str, folder: str = "INBOX", limit: int = 20) -> list:
        """Search emails via IMAP SEARCH."""
        if not self.can_receive:
            return [{"error": "IMAP not configured"}]

        try:
            imap = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
            imap.login(self.config.imap_user, self.config.imap_password)
            imap.select(folder)

            # IMAP search by subject or body
            _, nums = imap.search(None, f'(OR SUBJECT "{query}" BODY "{query}")')
            nums = nums[0].split()[-limit:]

            results = []
            for num in reversed(nums):
                _, msg_data = imap.fetch(num, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                results.append({
                    "from": msg.get("From", ""),
                    "subject": msg.get("Subject", ""),
                    "date": msg.get("Date", ""),
                    "channel": "email",
                })

            imap.logout()
            return results

        except Exception as e:
            log.error(f"IMAP search failed: {e}")
            return [{"error": str(e)}]
