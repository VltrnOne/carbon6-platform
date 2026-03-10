"""AEGIS-CONNECTIVITY - WiFi, Bluetooth, Cellular, Airplane, VPN control."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.connectivity")


class ConnectivityEngine(PushcutBridge):
    """Control and monitor all device connectivity."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="connectivity")

    def get_wifi_status(self) -> dict:
        """Get current WiFi network name and IP."""
        return self.execute_shortcut("AEGIS Get WiFi Status")

    def toggle_wifi(self, enabled: bool) -> dict:
        """Turn WiFi on or off."""
        return self.execute_shortcut("AEGIS Set WiFi", {"enabled": enabled})

    def get_bluetooth_status(self) -> dict:
        """Get Bluetooth state."""
        return self.execute_shortcut("AEGIS Get Bluetooth")

    def toggle_bluetooth(self, enabled: bool) -> dict:
        """Turn Bluetooth on or off."""
        return self.execute_shortcut("AEGIS Set Bluetooth", {"enabled": enabled})

    def get_cellular_status(self) -> dict:
        """Get carrier and cellular data info."""
        return self.execute_shortcut("AEGIS Get Cellular")

    def toggle_airplane_mode(self, enabled: bool) -> dict:
        """Toggle Airplane Mode."""
        return self.execute_shortcut("AEGIS Set Airplane Mode", {"enabled": enabled})

    def get_vpn_status(self) -> dict:
        """Check VPN connection status."""
        return self.execute_shortcut("AEGIS Get VPN Status")

    def get_full_status(self) -> dict:
        """Combined connectivity snapshot."""
        result = self.execute_shortcut("AEGIS Get Connectivity")
        if "error" not in result and self.db:
            self.db.store_snapshot("connectivity", result)
        return result
