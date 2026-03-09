"""Communications API - FastAPI webhook and REST endpoints.

Run: uvicorn communications_department.api.server:app --host 0.0.0.0 --port 3100
"""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from communications_department.engine.database import CommsDB
from communications_department.engine.sms import SMSEngine
from communications_department.engine.email_engine import EmailEngine
from communications_department.engine.voice import VoiceEngine
from communications_department.engine.contacts import ContactManager
from communications_department.engine.search import SearchEngine
from communications_department.engine.router import MessageRouter
from communications_department.engine.inbox import UnifiedInbox
from communications_department.engine.analytics import AnalyticsEngine
from communications_department.engine.imessage import IMessageEngine

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("hermes.api")

app = FastAPI(
    title="HERMES Communications API",
    description="Carbon6 Communications Department - Unified messaging API",
    version="1.0.0",
)

# Initialize engines
db = CommsDB()
sms = SMSEngine(db=db)
email_eng = EmailEngine(db=db)
voice = VoiceEngine(db=db)
imessage = IMessageEngine(db=db)
contacts = ContactManager(db=db)
search = SearchEngine(db=db, email_engine=email_eng)
router = MessageRouter(db=db, sms_engine=sms, email_engine=email_eng, voice_engine=voice, imessage_engine=imessage)
inbox = UnifiedInbox(db=db, email_engine=email_eng)
analytics = AnalyticsEngine(db=db)


# --- Pydantic models ---

class SMSSend(BaseModel):
    to: str
    body: str
    media_url: Optional[str] = None


class EmailSend(BaseModel):
    to: str
    subject: str
    body: str
    html: Optional[str] = None


class VoiceCall(BaseModel):
    to: str
    message: Optional[str] = None
    twiml: Optional[str] = None


class ContactCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    preferred_channel: str = "sms"
    tags: list = []
    groups: list = []


class SmartSend(BaseModel):
    to: str
    body: str
    channel: Optional[str] = None
    subject: Optional[str] = None
    priority: int = 5


# --- SMS endpoints ---

@app.post("/api/comms/sms/send")
async def sms_send(msg: SMSSend):
    contact = db.resolve_contact(msg.to)
    contact_id = contact["id"] if contact else None
    to = contact.get("phone", msg.to) if contact else msg.to
    return sms.send(to, msg.body, media_url=msg.media_url, contact_id=contact_id)


@app.post("/api/comms/sms/webhook")
async def sms_webhook(request: Request):
    """Twilio inbound SMS webhook."""
    form = await request.form()
    from_number = form.get("From", "")
    body = form.get("Body", "")
    media_urls = []
    num_media = int(form.get("NumMedia", "0"))
    for i in range(num_media):
        url = form.get(f"MediaUrl{i}")
        if url:
            media_urls.append(url)

    result = sms.process_inbound(from_number, body, media_urls)
    log.info(f"Inbound SMS from {from_number}: {body[:50]}")

    # Return TwiML response
    return JSONResponse(
        content={"status": "received"},
        headers={"Content-Type": "application/xml"},
    )


@app.get("/api/comms/sms/status/{sid}")
async def sms_status(sid: str):
    return sms.get_status(sid)


# --- Email endpoints ---

@app.post("/api/comms/email/send")
async def email_send(msg: EmailSend):
    contact = db.resolve_contact(msg.to)
    contact_id = contact["id"] if contact else None
    to = contact.get("email", msg.to) if contact else msg.to
    return email_eng.send(to, msg.subject, msg.body, html=msg.html, contact_id=contact_id)


@app.get("/api/comms/email/inbox")
async def email_inbox(limit: int = 20, unread: bool = False):
    return email_eng.fetch_inbox(limit=limit, unread_only=unread)


@app.get("/api/comms/email/search")
async def email_search(q: str, limit: int = 20):
    return email_eng.search_emails(q, limit=limit)


# --- Voice endpoints ---

@app.post("/api/comms/voice/call")
async def voice_call(req: VoiceCall):
    contact = db.resolve_contact(req.to)
    contact_id = contact["id"] if contact else None
    to = contact.get("phone", req.to) if contact else req.to
    return voice.call(to, twiml=req.twiml, message=req.message, contact_id=contact_id)


@app.get("/api/comms/voice/status/{sid}")
async def voice_status(sid: str):
    return voice.get_call_status(sid)


@app.post("/api/comms/voice/webhook")
async def voice_webhook(request: Request):
    """Twilio voice webhook - returns TwiML."""
    return JSONResponse(
        content={"twiml": "<Response><Say>Hello from Carbon6 Communications.</Say></Response>"},
        headers={"Content-Type": "application/xml"},
    )


# --- iMessage endpoints ---

class IMessageSend(BaseModel):
    to: str
    body: str


class IMessageInbound(BaseModel):
    sender: str = ""  # Shortcuts may use 'sender' or 'from'
    body: str = ""
    is_imessage: bool = True


@app.post("/api/comms/imessage/send")
async def imessage_send(msg: IMessageSend):
    contact = db.resolve_contact(msg.to)
    contact_id = contact["id"] if contact else None
    to = contact.get("phone", msg.to) if contact else msg.to
    return imessage.send(to, msg.body, contact_id=contact_id)


@app.post("/api/comms/imessage/inbound")
async def imessage_inbound(request: Request):
    """Webhook endpoint for iPhone Shortcuts automation to forward inbound messages."""
    try:
        data = await request.json()
    except Exception:
        data = {}

    from_number = data.get("from") or data.get("sender") or data.get("From") or ""
    body = data.get("body") or data.get("message") or data.get("Body") or ""
    is_imessage = data.get("is_imessage", True)

    result = imessage.process_inbound(from_number, body, is_imessage=is_imessage)
    log.info(f"Inbound iMessage from {from_number}: {body[:50]}")
    return result


@app.get("/api/comms/imessage/status")
async def imessage_status():
    return imessage.status()


@app.post("/api/comms/imessage/retry")
async def imessage_retry():
    """Retry queued messages (call when phone comes back online)."""
    results = imessage.retry_queued()
    return {"retried": len(results), "results": results}


# --- Smart Send (auto-route) ---

@app.post("/api/comms/send")
async def smart_send(msg: SmartSend):
    contact = db.resolve_contact(msg.to)
    contact_id = contact["id"] if contact else None
    to = msg.to
    if contact:
        to = contact.get("phone") or contact.get("email") or msg.to
    return router.route(to, msg.body, channel=msg.channel, subject=msg.subject,
                        contact_id=contact_id, priority=msg.priority)


# --- Inbox ---

@app.get("/api/comms/inbox")
async def get_inbox(channel: Optional[str] = None, unread: bool = False, limit: int = 50):
    return inbox.get(channel=channel, unread_only=unread, limit=limit)


@app.post("/api/comms/inbox/sync")
async def sync_inbox():
    return inbox.sync_email()


@app.post("/api/comms/inbox/{message_id}/read")
async def mark_read(message_id: int):
    return {"marked": inbox.mark_read(message_id)}


# --- Search ---

@app.get("/api/comms/search")
async def search_comms(q: str, channel: Optional[str] = None,
                       contact: Optional[str] = None, limit: int = 50):
    return search.search(q, channel=channel, contact=contact, limit=limit)


# --- Contacts ---

@app.get("/api/comms/contacts")
async def list_contacts(group: Optional[str] = None, tag: Optional[str] = None):
    return {"contacts": contacts.list_all(group=group, tag=tag)}


@app.post("/api/comms/contacts")
async def add_contact(c: ContactCreate):
    return contacts.add(c.name, phone=c.phone, email=c.email,
                        preferred_channel=c.preferred_channel,
                        tags=c.tags, groups=c.groups)


@app.get("/api/comms/contacts/{identifier}")
async def find_contact(identifier: str):
    result = contacts.find(identifier)
    if not result:
        raise HTTPException(status_code=404, detail="Contact not found")
    return result


@app.get("/api/comms/contacts/{identifier}/conversation")
async def contact_conversation(identifier: str, limit: int = 50):
    return contacts.get_conversation(identifier, limit=limit)


# --- Analytics ---

@app.get("/api/comms/analytics")
async def get_analytics(days: int = 30):
    return analytics.dashboard(days=days)


@app.get("/api/comms/analytics/contact/{identifier}")
async def contact_analytics(identifier: str):
    return analytics.contact_engagement(identifier)


# --- Setup Agent (auto-configure iPhone) ---

from communications_department.engine.setup_agent import HermesSetupAgent
from fastapi.responses import HTMLResponse, Response

setup_agent = HermesSetupAgent()


@app.get("/api/comms/setup", response_class=HTMLResponse)
async def setup_page():
    """Serve the iPhone setup page. Open this URL on your phone."""
    return setup_agent.generate_setup_page_html()


@app.post("/api/comms/setup/run")
async def run_setup():
    """Execute full automated setup."""
    return setup_agent.run_full_setup()


@app.get("/api/comms/setup/shortcut/send")
async def download_send_shortcut():
    """Download the 'HERMES Send Message' shortcut file."""
    data = setup_agent.generate_send_shortcut()
    return Response(
        content=data,
        media_type="application/x-apple-shortcut",
        headers={
            "Content-Disposition": 'attachment; filename="HERMES Send Message.shortcut"',
        },
    )


@app.get("/api/comms/setup/shortcut/receive")
async def download_receive_shortcut():
    """Download the 'HERMES Receive Message' shortcut file."""
    data = setup_agent.generate_receive_shortcut()
    return Response(
        content=data,
        media_type="application/x-apple-shortcut",
        headers={
            "Content-Disposition": 'attachment; filename="HERMES Receive Message.shortcut"',
        },
    )


@app.get("/api/comms/setup/verify")
async def verify_setup():
    """Verify Pushcut connection and device."""
    return setup_agent.verify_pushcut()


# --- Status ---

@app.get("/api/comms/status")
async def status():
    return {
        "agent": "HERMES",
        "department": "Communications",
        "channels": {
            "imessage": imessage.is_configured,
            "sms": sms.is_configured,
            "email_send": email_eng.can_send,
            "email_receive": email_eng.can_receive,
            "voice": voice.is_configured,
        },
        "queue_size": router.queue_size(),
        "imessage_queue": imessage.queue_size(),
    }


# --- Init endpoint ---

@app.post("/api/comms/init")
async def init_db():
    db.init_tables()
    return {"status": "initialized"}
