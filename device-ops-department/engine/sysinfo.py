"""AEGIS-SYSINFO - Device model, iOS version, brightness, diagnostics."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.sysinfo")


class SystemInfoEngine(PushcutBridge):
    """Query and control device system information."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="sysinfo")

    def get_device_info(self) -> dict:
        """Get device model, name, OS version, uptime."""
        result = self.execute_shortcut("AEGIS Get Device Info")
        if "error" not in result and self.db:
            self.db.store_snapshot("sysinfo", result)
        return result

    def get_screen_brightness(self) -> dict:
        """Get current screen brightness level."""
        return self.execute_shortcut("AEGIS Get Brightness")

    def set_screen_brightness(self, level: int) -> dict:
        """Set screen brightness (0-100)."""
        level = max(0, min(100, level))
        return self.execute_shortcut("AEGIS Set Brightness", {"level": level})

    def get_full_report(self) -> dict:
        """Comprehensive device report: info + battery + storage + connectivity."""
        return self.execute_shortcut("AEGIS Device Report")
