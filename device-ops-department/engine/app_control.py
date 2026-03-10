"""AEGIS-APPCONTROL - Launch apps, check usage, open URLs."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.appcontrol")


class AppControlEngine(PushcutBridge):
    """Control app launching and monitor app usage."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="appcontrol")

    def open_app(self, app_name: str) -> dict:
        """Open an app by name."""
        return self.execute_shortcut("AEGIS Open App", {"app": app_name})

    def get_app_usage(self) -> dict:
        """Get Screen Time per-app usage stats."""
        return self.execute_shortcut("AEGIS Get App Usage")

    def open_url(self, url: str) -> dict:
        """Open a URL on the device."""
        return self.execute_shortcut("AEGIS Open URL", {"url": url})

    def open_settings(self, page: str = "") -> dict:
        """Open a specific Settings page via URL scheme."""
        settings_url = f"prefs:root={page}" if page else "prefs:"
        return self.execute_shortcut("AEGIS Open URL", {"url": settings_url})
