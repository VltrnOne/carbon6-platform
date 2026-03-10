"""AEGIS-MEDIA - Volume, playback, camera, flashlight control."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.media")


class MediaEngine(PushcutBridge):
    """Control media playback, volume, camera, and flashlight."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="media")

    def set_volume(self, level: int) -> dict:
        """Set volume (0-100)."""
        level = max(0, min(100, level))
        return self.execute_shortcut("AEGIS Set Volume", {"level": level})

    def get_volume(self) -> dict:
        """Get current volume level."""
        return self.execute_shortcut("AEGIS Get Volume")

    def play_sound(self, sound_name: str = "default") -> dict:
        """Play a sound on the device."""
        return self.execute_shortcut("AEGIS Play Sound", {"sound": sound_name})

    def toggle_playback(self, action: str = "playpause") -> dict:
        """Control media playback: play, pause, playpause, next, previous."""
        return self.execute_shortcut("AEGIS Media Control", {"action": action})

    def get_now_playing(self) -> dict:
        """Get currently playing media info."""
        return self.execute_shortcut("AEGIS Get Now Playing")

    def take_photo(self, camera: str = "back") -> dict:
        """Take a photo with front or back camera."""
        return self.execute_shortcut("AEGIS Take Photo", {"camera": camera})

    def set_flashlight(self, enabled: bool) -> dict:
        """Toggle flashlight on/off."""
        return self.execute_shortcut("AEGIS Set Flashlight", {"enabled": enabled})
