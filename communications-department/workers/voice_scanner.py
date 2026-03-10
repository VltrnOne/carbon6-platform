#!/usr/bin/env python3
"""Voice Drop Scanner - Auto-processes audio files from a watched folder.

Scans the voice-drop/inbox/ folder every N minutes for new audio files.
Transcribes each file → parses as HERMES command → executes → moves to processed/.

Drop folder structure:
    voice-drop/
        inbox/       ← Drop audio files here (.wav, .mp3, .m4a, .ogg, .webm)
        processed/   ← Successfully processed files move here
        failed/      ← Failed files move here with .error log

Usage:
    python3 voice_scanner.py                  # Run once
    python3 voice_scanner.py --watch          # Run continuously (5 min interval)
    python3 voice_scanner.py --interval 120   # Custom interval in seconds

Can also run via PM2:
    pm2 start voice_scanner.py --name hermes-voice-scanner -- --watch
"""
import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from communications_department.hermes import Hermes
from communications_department.engine.voice_command import VoiceCommander

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VOICE-SCANNER] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("voice_scanner")

# Supported audio extensions
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".aac", ".wma"}

# Default paths
BASE_DIR = Path(__file__).parent.parent / "voice-drop"
INBOX_DIR = BASE_DIR / "inbox"
PROCESSED_DIR = BASE_DIR / "processed"
FAILED_DIR = BASE_DIR / "failed"

# Default scan interval (seconds)
DEFAULT_INTERVAL = 300  # 5 minutes


def ensure_dirs():
    """Create drop folders if they don't exist."""
    for d in [INBOX_DIR, PROCESSED_DIR, FAILED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def scan_once(hermes: Hermes, voice_cmd: VoiceCommander) -> list:
    """Scan inbox for audio files, process each one."""
    ensure_dirs()
    results = []

    # Get all audio files sorted by modification time (oldest first)
    audio_files = sorted(
        [f for f in INBOX_DIR.iterdir()
         if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS],
        key=lambda f: f.stat().st_mtime,
    )

    if not audio_files:
        return results

    log.info(f"Found {len(audio_files)} audio file(s) to process")

    for audio_file in audio_files:
        result = process_file(audio_file, hermes, voice_cmd)
        results.append(result)

    return results


def process_file(audio_file: Path, hermes: Hermes, voice_cmd: VoiceCommander) -> dict:
    """Process a single audio file: transcribe → execute → move."""
    log.info(f"Processing: {audio_file.name}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    try:
        # Transcribe
        text = voice_cmd.transcribe_file(str(audio_file))
        if not text:
            raise ValueError("Transcription returned empty result")

        log.info(f"Transcribed: '{text}'")

        # Execute as command
        result = voice_cmd.execute(text)
        log.info(f"Executed: {json.dumps(result, default=str)[:200]}")

        # Move to processed
        dest = PROCESSED_DIR / f"{timestamp}_{audio_file.name}"
        shutil.move(str(audio_file), str(dest))

        # Write result log alongside
        log_file = dest.with_suffix(dest.suffix + ".result.json")
        log_file.write_text(json.dumps({
            "file": audio_file.name,
            "transcription": text,
            "result": result,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2, default=str))

        return {"file": audio_file.name, "transcription": text, "result": result, "status": "ok"}

    except Exception as e:
        log.error(f"Failed to process {audio_file.name}: {e}")

        # Move to failed
        dest = FAILED_DIR / f"{timestamp}_{audio_file.name}"
        shutil.move(str(audio_file), str(dest))

        # Write error log
        err_file = dest.with_suffix(dest.suffix + ".error")
        err_file.write_text(f"Error: {e}\nTimestamp: {datetime.now(timezone.utc).isoformat()}\n")

        return {"file": audio_file.name, "error": str(e), "status": "failed"}


def watch(interval: int = DEFAULT_INTERVAL):
    """Continuously watch the inbox folder."""
    log.info(f"Voice scanner started — watching {INBOX_DIR}")
    log.info(f"Scan interval: {interval}s ({interval // 60}m)")
    log.info(f"Drop audio files in: {INBOX_DIR}")

    hermes = Hermes()
    voice_cmd = VoiceCommander(hermes=hermes)

    if not voice_cmd.is_configured:
        log.error("No STT engine configured! Set OPENAI_API_KEY or install openai-whisper")
        sys.exit(1)

    log.info(f"STT engine: {voice_cmd.active_engine}")

    while True:
        try:
            results = scan_once(hermes, voice_cmd)
            if results:
                ok = sum(1 for r in results if r["status"] == "ok")
                fail = sum(1 for r in results if r["status"] == "failed")
                log.info(f"Batch complete: {ok} processed, {fail} failed")
        except Exception as e:
            log.error(f"Scan error: {e}")

        time.sleep(interval)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="HERMES Voice Drop Scanner")
    parser.add_argument("--watch", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                        help=f"Scan interval in seconds (default: {DEFAULT_INTERVAL})")
    args = parser.parse_args()

    if args.watch:
        watch(interval=args.interval)
    else:
        hermes = Hermes()
        voice_cmd = VoiceCommander(hermes=hermes)
        results = scan_once(hermes, voice_cmd)
        print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
