"""AEGIS-CLIPBOARD - Remote clipboard get/set."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.clipboard")


class ClipboardEngine(PushcutBridge):
    """Remote clipboard access - read and write iPhone clipboard."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="clipboard")

    def get(self) -> dict:
        """Get current clipboard content."""
        return self.execute_shortcut("AEGIS Get Clipboard")

    def set(self, content: str) -> dict:
        """Set clipboard content on the device."""
        return self.execute_shortcut("AEGIS Set Clipboard", {"content": content})
