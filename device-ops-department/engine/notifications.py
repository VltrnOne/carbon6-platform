"""AEGIS-NOTIFICATIONS - Focus/DND modes and push notifications."""
import logging
import requests
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.notifications")


class NotificationsEngine(PushcutBridge):
    """Manage Focus modes and send notifications to device."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="notifications")

    def get_focus_mode(self) -> dict:
        """Get current Focus/DND status."""
        return self.execute_shortcut("AEGIS Get Focus Mode")

    def set_focus_mode(self, mode: str, enabled: bool) -> dict:
        """Set a Focus mode (Do Not Disturb, Work, Sleep, etc)."""
        result = self.execute_shortcut("AEGIS Set Focus Mode",
                                       {"mode": mode, "enabled": enabled})
        if "error" not in result and self.db:
            self.db.store_event("focus_mode_changed", data={"mode": mode, "enabled": enabled})
        return result

    def send_notification(self, title: str, body: str = "") -> dict:
        """Send a push notification to the device via Pushcut notification API."""
        if not self.api_key:
            return {"error": "Pushcut not configured"}

        try:
            resp = requests.post(
                f"{self.base_url}/v1/notifications/{title}",
                headers={"API-Key": self.api_key},
                json={"text": body} if body else {},
                timeout=10,
            )
            return {"status": "sent" if resp.status_code == 200 else "failed",
                    "code": resp.status_code}
        except Exception as e:
            return {"error": str(e)}

    def get_notification_summary(self) -> dict:
        """Get pending notification count (limited by iOS)."""
        return self.execute_shortcut("AEGIS Get Notifications")
