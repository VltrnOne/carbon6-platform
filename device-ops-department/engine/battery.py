"""AEGIS-BATTERY - Battery monitoring and low power mode control."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.battery")


class BatteryEngine(PushcutBridge):
    """Monitor battery level, charging status, and low power mode."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="battery")

    def get_status(self) -> dict:
        """Get full battery status: level, charging, low power mode."""
        result = self.execute_shortcut("AEGIS Get Battery Status")
        if "error" not in result and self.db:
            self.db.store_snapshot("battery", result)
            level = result.get("level")
            if level is not None and level <= self.config.monitor.battery_alert_threshold:
                self.db.store_event("battery_low", severity="warning",
                                    data={"level": level})
        return result

    def get_level(self) -> dict:
        """Get battery level percentage."""
        return self.execute_shortcut("AEGIS Get Battery Level")

    def set_low_power_mode(self, enabled: bool) -> dict:
        """Toggle Low Power Mode."""
        return self.execute_shortcut("AEGIS Set Low Power Mode",
                                     {"enabled": enabled})

    def get_charging_state(self) -> dict:
        """Check if device is charging."""
        status = self.get_status()
        return {
            "charging": status.get("charging", False),
            "level": status.get("level"),
        }
