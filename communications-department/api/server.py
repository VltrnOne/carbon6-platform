"""Communications API - FastAPI webhook and REST endpoints.

Run: uvicorn communications_department.api.server:app --host 0.0.0.0 --port 3100
"""
import json
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pathlib import Path

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from communications_department.engine.campaign import CampaignEngine
from communications_department.engine.voice_command import VoiceCommander

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
campaigns = CampaignEngine(db=db, contacts=contacts, router=router)
voice_cmd = VoiceCommander()


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


# --- Campaign endpoints ---

class CampaignCreate(BaseModel):
    name: str
    body: str
    target_type: str  # single, group, tag, all
    target_value: Optional[str] = None
    channel: str = "sms"
    subject: Optional[str] = None
    template_id: Optional[int] = None
    scheduled_at: Optional[str] = None


class CampaignSend(BaseModel):
    throttle_rate: Optional[float] = None


@app.post("/api/comms/campaigns")
async def create_campaign(c: CampaignCreate):
    """Create a new campaign (draft or scheduled)."""
    sched = None
    if c.scheduled_at:
        from datetime import datetime as dt
        sched = dt.fromisoformat(c.scheduled_at)
    return campaigns.create(
        name=c.name, body=c.body, target_type=c.target_type,
        target_value=c.target_value, channel=c.channel,
        subject=c.subject, template_id=c.template_id,
        scheduled_at=sched,
    )


@app.get("/api/comms/campaigns")
async def list_campaigns(status: Optional[str] = None):
    return campaigns.list(status=status)


@app.get("/api/comms/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    result = campaigns.read(campaign_id)
    if result and result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/api/comms/campaigns/{campaign_id}/preview")
async def preview_campaign(campaign_id: int):
    return campaigns.preview(campaign_id)


@app.post("/api/comms/campaigns/{campaign_id}/send")
async def send_campaign(campaign_id: int, opts: CampaignSend = None):
    """Send a campaign to all its recipients."""
    throttle = opts.throttle_rate if opts else None
    return campaigns.send(campaign_id, throttle_rate=throttle)


@app.post("/api/comms/campaigns/{campaign_id}/cancel")
async def cancel_campaign(campaign_id: int):
    return campaigns.cancel(campaign_id)


@app.post("/api/comms/campaigns/{campaign_id}/duplicate")
async def duplicate_campaign(campaign_id: int, name: Optional[str] = None):
    return campaigns.duplicate(campaign_id, new_name=name)


# --- Voice Command endpoints ---

class VoiceTextCommand(BaseModel):
    text: str


@app.post("/api/comms/voice/command")
async def voice_text_command(cmd: VoiceTextCommand):
    """Execute a text command through the voice command parser.
    Accepts natural language like: 'create a campaign called X for group Y saying Z'
    """
    # Use a temporary Hermes instance for voice command execution
    from communications_department.hermes import Hermes
    hermes = Hermes()
    vc = VoiceCommander(hermes=hermes)
    return vc.execute(cmd.text)


@app.post("/api/comms/voice/transcribe")
async def voice_transcribe(request: Request):
    """Upload audio file for transcription + command execution.

    Send audio as multipart form data with field name 'audio'.
    Supported: .wav, .mp3, .m4a, .ogg, .webm
    """
    import tempfile
    form = await request.form()
    audio_file = form.get("audio")
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided. Upload as 'audio' field.")

    contents = await audio_file.read()
    filename = getattr(audio_file, "filename", "audio.wav")

    text = voice_cmd.transcribe_bytes(contents, filename=filename)
    if not text:
        return {"error": "Could not transcribe audio. Check STT engine configuration."}

    # Execute the transcribed command
    from communications_department.hermes import Hermes
    hermes = Hermes()
    vc = VoiceCommander(hermes=hermes)
    result = vc.execute(text)
    return result


@app.get("/api/comms/voice/status")
async def voice_command_status():
    return voice_cmd.status()


@app.post("/api/comms/voice/scan")
async def voice_scan_now():
    """Manually trigger a scan of the voice drop inbox folder."""
    from communications_department.workers.voice_scanner import scan_once, INBOX_DIR, PROCESSED_DIR, FAILED_DIR
    from communications_department.hermes import Hermes
    hermes = Hermes()
    vc = VoiceCommander(hermes=hermes)
    results = scan_once(hermes, vc)
    return {"scanned": len(results), "results": results}


@app.get("/api/comms/voice/drop-status")
async def voice_drop_status():
    """Get voice drop folder status."""
    from communications_department.workers.voice_scanner import INBOX_DIR, PROCESSED_DIR, FAILED_DIR, AUDIO_EXTENSIONS
    def count_audio(d):
        if not d.exists():
            return 0
        return len([f for f in d.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS])
    def list_files(d, limit=20):
        if not d.exists():
            return []
        files = sorted(
            [f for f in d.iterdir() if f.is_file()],
            key=lambda f: f.stat().st_mtime, reverse=True,
        )[:limit]
        return [{"name": f.name, "size": f.stat().st_size,
                 "modified": f.stat().st_mtime} for f in files]
    return {
        "inbox": {"path": str(INBOX_DIR), "audio_files": count_audio(INBOX_DIR), "files": list_files(INBOX_DIR)},
        "processed": {"path": str(PROCESSED_DIR), "count": len(list(PROCESSED_DIR.iterdir())) if PROCESSED_DIR.exists() else 0, "recent": list_files(PROCESSED_DIR, 10)},
        "failed": {"path": str(FAILED_DIR), "count": len(list(FAILED_DIR.iterdir())) if FAILED_DIR.exists() else 0, "recent": list_files(FAILED_DIR, 10)},
    }


# --- Command Center UI ---

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/command", response_class=HTMLResponse)
@app.get("/cmd", response_class=HTMLResponse)
async def command_center_ui():
    """Serve the HERMES Command Center UI."""
    html_path = STATIC_DIR / "command.html"
    return HTMLResponse(content=html_path.read_text())


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
