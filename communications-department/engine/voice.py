"""Voice Engine - Outbound calls, voicemail, and transcription via Twilio."""
import logging
from ..config.settings import load_config

log = logging.getLogger("hermes.voice")


class VoiceEngine:
    """Handles voice calls via Twilio."""

    def __init__(self, db=None):
        self.config = load_config().twilio
        self.db = db
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from twilio.rest import Client
            self._client = Client(self.config.account_sid, self.config.auth_token)
        return self._client

    @property
    def is_configured(self) -> bool:
        return self.config.is_configured

    def call(self, to: str, twiml: str = None, message: str = None,
             contact_id: int = None) -> dict:
        """Initiate an outbound voice call.

        Args:
            to: Phone number to call
            twiml: Raw TwiML for call flow
            message: Text-to-speech message (creates TwiML automatically)
            contact_id: Optional contact ID for tracking
        """
        if not self.is_configured:
            return {"error": "Twilio not configured"}

        if message and not twiml:
            twiml = f'<Response><Say voice="alice">{message}</Say></Response>'

        kwargs = {
            "to": to,
            "from_": self.config.phone_number,
        }

        if twiml:
            kwargs["twiml"] = twiml
        elif self.config.webhook_url:
            kwargs["url"] = f"{self.config.webhook_url}/api/comms/voice/twiml"
        else:
            kwargs["twiml"] = '<Response><Say voice="alice">Hello from Carbon6 Communications.</Say></Response>'

        try:
            call = self.client.calls.create(**kwargs)
            result = {
                "sid": call.sid,
                "status": call.status,
                "to": to,
                "channel": "voice",
            }

            if self.db:
                self.db.store_message(
                    channel="voice", direction="outbound",
                    from_addr=self.config.phone_number, to_addr=to,
                    body=message or "[voice call]",
                    contact_id=contact_id, status=call.status,
                    provider_sid=call.sid,
                )

            log.info(f"Call initiated to {to}: {call.sid}")
            return result

        except Exception as e:
            log.error(f"Call failed to {to}: {e}")
            return {"error": str(e)}

    def get_call_status(self, sid: str) -> dict:
        """Get status of a call."""
        if not self.is_configured:
            return {"error": "Twilio not configured"}
        try:
            call = self.client.calls(sid).fetch()
            return {
                "sid": call.sid, "status": call.status,
                "duration": call.duration, "to": call.to,
                "start_time": call.start_time.isoformat() if call.start_time else None,
            }
        except Exception as e:
            return {"error": str(e)}

    def get_recordings(self, call_sid: str = None, limit: int = 10) -> list:
        """Get call recordings."""
        if not self.is_configured:
            return []
        try:
            kwargs = {"limit": limit}
            if call_sid:
                kwargs["call_sid"] = call_sid
            recordings = self.client.recordings.list(**kwargs)
            return [
                {
                    "sid": r.sid, "call_sid": r.call_sid,
                    "duration": r.duration, "status": r.status,
                    "uri": r.uri,
                }
                for r in recordings
            ]
        except Exception as e:
            log.error(f"Failed to fetch recordings: {e}")
            return []

    def get_transcriptions(self, recording_sid: str = None) -> list:
        """Get transcriptions for recordings."""
        if not self.is_configured:
            return []
        try:
            transcriptions = self.client.transcriptions.list(limit=20)
            if recording_sid:
                transcriptions = [t for t in transcriptions if t.recording_sid == recording_sid]
            return [
                {
                    "sid": t.sid, "recording_sid": t.recording_sid,
                    "status": t.status,
                    "transcription_text": t.transcription_text,
                }
                for t in transcriptions
            ]
        except Exception as e:
            log.error(f"Failed to fetch transcriptions: {e}")
            return []
