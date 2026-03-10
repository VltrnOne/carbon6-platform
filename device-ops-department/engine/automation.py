"""AEGIS-AUTOMATION - Run arbitrary shortcuts, schedule automations."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.automation")


class AutomationEngine(PushcutBridge):
    """Execute and manage Apple Shortcuts - the meta-agent."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="automation")

    def list_shortcuts(self) -> dict:
        """Get list of all Shortcuts on the iPhone."""
        return self.execute_shortcut("AEGIS List Shortcuts")

    def run_shortcut(self, name: str, input_data: dict = None) -> dict:
        """Run any Apple Shortcut by name with optional input."""
        result = self.execute_shortcut(name, input_data)
        if self.db:
            self.db.store_event("shortcut_executed", data={"name": name})
        return result

    def schedule_shortcut(self, name: str, delay: str = None) -> dict:
        """Schedule a shortcut execution with delay (e.g., '10m', '1h')."""
        params = {"shortcut": name}
        if delay:
            params["delay"] = delay
        return self.execute_shortcut(name, delay=delay)

    def create_pushcut_action(self, name: str, shortcut: str) -> dict:
        """Register a named action in Pushcut that maps to a shortcut."""
        import requests
        try:
            resp = requests.post(
                f"{self.base_url}/v1/actions",
                headers={"API-Key": self.api_key},
                json={"name": name, "shortcut": shortcut},
                timeout=10,
            )
            return resp.json() if resp.text else {"status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
