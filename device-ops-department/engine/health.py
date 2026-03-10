"""AEGIS-HEALTH - Steps, screen time, and motion data."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.health")


class HealthEngine(PushcutBridge):
    """Access health and activity data from iPhone sensors."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="health")

    def get_steps(self, date: str = "today") -> dict:
        """Get step count for a date (default: today)."""
        result = self.execute_shortcut("AEGIS Get Steps", {"date": date})
        if "error" not in result and self.db:
            self.db.store_snapshot("steps", result)
        return result

    def get_screen_time(self) -> dict:
        """Get screen time data."""
        return self.execute_shortcut("AEGIS Get Screen Time")

    def get_motion_data(self) -> dict:
        """Get current motion activity (walking/driving/stationary)."""
        return self.execute_shortcut("AEGIS Get Motion")
