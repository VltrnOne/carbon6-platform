"""Voice Command Interface - Speech-to-text command input for HERMES.

Accepts voice input via microphone or audio file, transcribes to text,
then parses and executes as a HERMES command.

Supports:
- Live microphone input (push-to-talk or continuous)
- Audio file input (.wav, .mp3, .m4a, .ogg, .webm)
- OpenAI Whisper API (cloud, most accurate)
- Local whisper model (offline, via openai-whisper package)
- Deepgram API (alternative, real-time streaming)

Usage:
    from voice_command import VoiceCommander
    vc = VoiceCommander(hermes)
    result = vc.listen()           # mic input → transcribe → execute
    result = vc.from_file("cmd.wav")  # file → transcribe → execute
    text = vc.transcribe_file("audio.wav")  # just transcribe, don't execute
"""
import io
import json
import logging
import os
import subprocess
import tempfile
from typing import Optional

log = logging.getLogger("hermes.voice_command")


class VoiceCommander:
    """Converts voice to HERMES commands via speech-to-text."""

    def __init__(self, hermes=None, engine: str = "auto"):
        """
        Args:
            hermes: Hermes instance for executing commands
            engine: 'whisper_api' (OpenAI), 'whisper_local', 'deepgram', or 'auto'
        """
        self.hermes = hermes
        self.engine = engine
        self._openai_key = os.getenv("OPENAI_API_KEY", "")
        self._deepgram_key = os.getenv("DEEPGRAM_API_KEY", "")

    @property
    def is_configured(self) -> bool:
        """Check if at least one STT engine is available."""
        if self._openai_key:
            return True
        if self._deepgram_key:
            return True
        # Check for local whisper
        try:
            import whisper  # noqa: F401
            return True
        except ImportError:
            pass
        return False

    @property
    def active_engine(self) -> str:
        """Determine which engine to use."""
        if self.engine != "auto":
            return self.engine
        if self._openai_key:
            return "whisper_api"
        if self._deepgram_key:
            return "deepgram"
        try:
            import whisper  # noqa: F401
            return "whisper_local"
        except ImportError:
            pass
        return "none"

    def listen(self, duration: int = 5, prompt: str = None) -> dict:
        """Record from microphone, transcribe, and execute as command.

        Args:
            duration: Recording duration in seconds
            prompt: Optional Whisper prompt hint for better accuracy
        """
        audio_path = self._record_mic(duration)
        if not audio_path:
            return {"error": "Failed to record audio. Is a microphone available?"}

        try:
            text = self.transcribe_file(audio_path, prompt=prompt)
            if not text:
                return {"error": "Could not transcribe audio. Try speaking louder or clearer."}

            result = self.execute(text)
            return result
        finally:
            if os.path.exists(audio_path):
                os.unlink(audio_path)

    def from_file(self, file_path: str, prompt: str = None) -> dict:
        """Transcribe an audio file and execute as command."""
        if not os.path.exists(file_path):
            return {"error": f"Audio file not found: {file_path}"}

        text = self.transcribe_file(file_path, prompt=prompt)
        if not text:
            return {"error": "Could not transcribe audio file."}

        return self.execute(text)

    def from_text(self, text: str) -> dict:
        """Parse and execute a text command (same pipeline as voice, without STT)."""
        return self.execute(text)

    def execute(self, text: str) -> dict:
        """Parse transcribed text into a HERMES command and execute it.

        Understands natural language like:
        - "create a campaign called Spring Sale for the VIP group saying 20% off everything"
        - "send campaign 5"
        - "read campaign 3"
        - "text John hey what's up"
        - "broadcast to sales new product launch"
        """
        if not self.hermes:
            return {"error": "No HERMES instance configured", "transcription": text}

        log.info(f"Voice command: '{text}'")

        # Try campaign-specific parsing first
        campaign_result = self._parse_campaign_command(text)
        if campaign_result:
            return {**campaign_result, "transcription": text, "source": "voice"}

        # Fall through to standard HERMES command parsing
        args = text.strip().split()
        result = self.hermes.handle_command(args)
        return {**result, "transcription": text, "source": "voice"}

    def transcribe_file(self, file_path: str, prompt: str = None) -> Optional[str]:
        """Transcribe an audio file to text."""
        engine = self.active_engine

        if engine == "whisper_api":
            return self._transcribe_whisper_api(file_path, prompt)
        elif engine == "whisper_local":
            return self._transcribe_whisper_local(file_path, prompt)
        elif engine == "deepgram":
            return self._transcribe_deepgram(file_path)
        else:
            log.error("No STT engine available. Set OPENAI_API_KEY or install openai-whisper.")
            return None

    def transcribe_bytes(self, audio_bytes: bytes, filename: str = "audio.wav",
                         prompt: str = None) -> Optional[str]:
        """Transcribe raw audio bytes."""
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(filename)[1], delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            return self.transcribe_file(tmp_path, prompt=prompt)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def status(self) -> dict:
        """Get voice command system status."""
        return {
            "configured": self.is_configured,
            "engine": self.active_engine,
            "openai_key_set": bool(self._openai_key),
            "deepgram_key_set": bool(self._deepgram_key),
            "whisper_local": self._check_whisper_local(),
            "mic_available": self._check_mic(),
        }

    # --- STT Engines ---

    def _transcribe_whisper_api(self, file_path: str, prompt: str = None) -> Optional[str]:
        """Transcribe via OpenAI Whisper API."""
        try:
            import httpx
        except ImportError:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self._openai_key)
                with open(file_path, "rb") as f:
                    response = client.audio.transcriptions.create(
                        model="whisper-1", file=f,
                        prompt=prompt or "HERMES campaign text send broadcast contacts",
                        language="en",
                    )
                return response.text.strip()
            except Exception as e:
                log.error(f"Whisper API (openai lib) failed: {e}")
                return None

        # Use httpx directly if openai package not installed
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "audio/wav")}
                data = {
                    "model": "whisper-1",
                    "language": "en",
                    "prompt": prompt or "HERMES campaign text send broadcast contacts",
                }
                resp = httpx.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {self._openai_key}"},
                    files=files, data=data, timeout=30,
                )
                resp.raise_for_status()
                return resp.json().get("text", "").strip()
        except Exception as e:
            log.error(f"Whisper API (httpx) failed: {e}")
            return None

    def _transcribe_whisper_local(self, file_path: str, prompt: str = None) -> Optional[str]:
        """Transcribe using local whisper model."""
        try:
            import whisper
            model = whisper.load_model("base")  # base is a good balance of speed/accuracy
            result = model.transcribe(
                file_path,
                language="en",
                initial_prompt=prompt or "HERMES campaign text send broadcast",
            )
            return result.get("text", "").strip()
        except Exception as e:
            log.error(f"Local whisper failed: {e}")
            return None

    def _transcribe_deepgram(self, file_path: str) -> Optional[str]:
        """Transcribe via Deepgram API."""
        try:
            import httpx
            with open(file_path, "rb") as f:
                resp = httpx.post(
                    "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true",
                    headers={
                        "Authorization": f"Token {self._deepgram_key}",
                        "Content-Type": "audio/wav",
                    },
                    content=f.read(), timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return (
                    data.get("results", {})
                    .get("channels", [{}])[0]
                    .get("alternatives", [{}])[0]
                    .get("transcript", "")
                    .strip()
                )
        except Exception as e:
            log.error(f"Deepgram failed: {e}")
            return None

    # --- Mic Recording ---

    def _record_mic(self, duration: int = 5) -> Optional[str]:
        """Record from microphone using sox/arecord/ffmpeg."""
        tmp_path = tempfile.mktemp(suffix=".wav")

        # Try sox (rec command)
        try:
            subprocess.run(
                ["rec", "-q", "-r", "16000", "-c", "1", "-b", "16", tmp_path,
                 "trim", "0", str(duration)],
                check=True, timeout=duration + 5,
                capture_output=True,
            )
            return tmp_path
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        # Try arecord (ALSA)
        try:
            subprocess.run(
                ["arecord", "-q", "-f", "S16_LE", "-r", "16000", "-c", "1",
                 "-d", str(duration), tmp_path],
                check=True, timeout=duration + 5,
                capture_output=True,
            )
            return tmp_path
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        # Try ffmpeg
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-f", "pulse", "-i", "default",
                 "-ar", "16000", "-ac", "1", "-t", str(duration), tmp_path],
                check=True, timeout=duration + 5,
                capture_output=True,
            )
            return tmp_path
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        log.error("No audio recording tool found (tried: sox/rec, arecord, ffmpeg)")
        return None

    def _check_mic(self) -> bool:
        """Check if a microphone is available."""
        try:
            result = subprocess.run(
                ["arecord", "-l"], capture_output=True, text=True, timeout=5
            )
            return "card" in result.stdout.lower()
        except Exception:
            return False

    def _check_whisper_local(self) -> bool:
        try:
            import whisper  # noqa: F401
            return True
        except ImportError:
            return False

    # --- Campaign Command Parsing ---

    def _parse_campaign_command(self, text: str) -> Optional[dict]:
        """Parse natural language campaign commands."""
        lower = text.lower().strip()

        # "create a campaign..." / "new campaign..."
        if any(lower.startswith(p) for p in [
            "create a campaign", "create campaign", "new campaign",
            "make a campaign", "start a campaign",
        ]):
            return self._parse_create_campaign(text)

        # "send campaign <id>" / "launch campaign <id>"
        if any(lower.startswith(p) for p in [
            "send campaign", "launch campaign", "fire campaign", "blast campaign",
        ]):
            return self._parse_send_campaign(text)

        # "read campaign <id>" / "show campaign <id>" / "campaign status"
        if any(lower.startswith(p) for p in [
            "read campaign", "show campaign", "view campaign",
            "campaign status", "check campaign", "get campaign",
        ]):
            return self._parse_read_campaign(text)

        # "list campaigns" / "show campaigns"
        if any(p in lower for p in [
            "list campaigns", "show campaigns", "all campaigns",
            "my campaigns", "show all campaigns",
        ]):
            return self.hermes.campaigns.list()

        # "cancel campaign <id>"
        if any(lower.startswith(p) for p in ["cancel campaign", "stop campaign"]):
            return self._parse_cancel_campaign(text)

        return None

    def _parse_create_campaign(self, text: str) -> dict:
        """Parse: 'create a campaign called X for group Y saying Z'"""
        lower = text.lower()

        # Extract name (after "called" or "named")
        name = None
        for marker in ["called ", "named "]:
            if marker in lower:
                rest = text[lower.index(marker) + len(marker):]
                # Name goes until next keyword
                for stop in [" for ", " to ", " targeting ", " saying ", " with message ", " body "]:
                    if stop in rest.lower():
                        name = rest[:rest.lower().index(stop)].strip()
                        break
                if not name:
                    name = rest.strip()
                break

        if not name:
            name = f"Campaign {int(__import__('time').time())}"

        # Extract target
        target_type = "all"
        target_value = None

        if " for all" in lower or " to all" in lower or " to everyone" in lower:
            target_type = "all"
        elif " for group " in lower or " to group " in lower:
            for marker in ["for group ", "to group "]:
                if marker in lower:
                    rest = text[lower.index(marker) + len(marker):]
                    for stop in [" saying ", " with message ", " body ", " message "]:
                        if stop in rest.lower():
                            target_value = rest[:rest.lower().index(stop)].strip()
                            break
                    if not target_value:
                        target_value = rest.split()[0].strip()
                    target_type = "group"
                    break
        elif " for tag " in lower or " to tag " in lower:
            for marker in ["for tag ", "to tag "]:
                if marker in lower:
                    rest = text[lower.index(marker) + len(marker):]
                    for stop in [" saying ", " with message ", " body ", " message "]:
                        if stop in rest.lower():
                            target_value = rest[:rest.lower().index(stop)].strip()
                            break
                    if not target_value:
                        target_value = rest.split()[0].strip()
                    target_type = "tag"
                    break
        elif " for " in lower or " to " in lower:
            # Single contact
            for marker in ["for ", "to "]:
                if marker in lower:
                    rest = text[lower.index(marker) + len(marker):]
                    for stop in [" saying ", " with message ", " body ", " message "]:
                        if stop in rest.lower():
                            target_value = rest[:rest.lower().index(stop)].strip()
                            break
                    if not target_value:
                        target_value = rest.split()[0].strip()
                    # Check if it's a group reference
                    if target_value.lower() in ("all", "everyone", "everybody"):
                        target_type = "all"
                        target_value = None
                    else:
                        target_type = "single"
                    break

        # Extract message body
        body = None
        for marker in ["saying ", "with message ", "body ", "message "]:
            if marker in lower:
                idx = lower.index(marker) + len(marker)
                body = text[idx:].strip().strip('"').strip("'")
                break

        if not body:
            return {"error": "Could not parse campaign message. Try: 'create campaign called X for group Y saying Z'"}

        return self.hermes.campaigns.create(
            name=name, body=body,
            target_type=target_type, target_value=target_value,
        )

    def _parse_send_campaign(self, text: str) -> dict:
        """Parse: 'send campaign 5' or 'send campaign Spring Sale'"""
        parts = text.strip().split()
        # Find campaign ID or name after 'campaign'
        if "campaign" in [p.lower() for p in parts]:
            idx = [p.lower() for p in parts].index("campaign")
            rest = parts[idx + 1:]
            if rest and rest[0].isdigit():
                return self.hermes.campaigns.send(int(rest[0]))
            elif rest:
                # Try to find by name
                name = " ".join(rest)
                campaigns = self.hermes.campaigns.list().get("campaigns", [])
                for c in campaigns:
                    if c["name"].lower() == name.lower():
                        return self.hermes.campaigns.send(c["id"])
                return {"error": f"Campaign '{name}' not found"}
        return {"error": "Specify campaign ID or name: 'send campaign 5'"}

    def _parse_read_campaign(self, text: str) -> dict:
        """Parse: 'read campaign 3'"""
        parts = text.strip().split()
        if "campaign" in [p.lower() for p in parts]:
            idx = [p.lower() for p in parts].index("campaign")
            rest = parts[idx + 1:]
            if rest and rest[0].isdigit():
                return self.hermes.campaigns.read(int(rest[0]))
            elif rest:
                name = " ".join(rest)
                campaigns = self.hermes.campaigns.list().get("campaigns", [])
                for c in campaigns:
                    if c["name"].lower() == name.lower():
                        return self.hermes.campaigns.read(c["id"])
                return {"error": f"Campaign '{name}' not found"}
        return {"error": "Specify campaign ID: 'read campaign 3'"}

    def _parse_cancel_campaign(self, text: str) -> dict:
        """Parse: 'cancel campaign 5'"""
        parts = text.strip().split()
        if "campaign" in [p.lower() for p in parts]:
            idx = [p.lower() for p in parts].index("campaign")
            rest = parts[idx + 1:]
            if rest and rest[0].isdigit():
                return self.hermes.campaigns.cancel(int(rest[0]))
        return {"error": "Specify campaign ID: 'cancel campaign 5'"}
