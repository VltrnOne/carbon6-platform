#!/usr/bin/env python3
"""AEGIS - Advanced Electronics Guardian & Intelligence System.

Lead agent CLI for the Device Operations Department.
Controls all iPhone functions via Pushcut + Apple Shortcuts.

Usage:
    aegis battery                  # Battery status
    aegis battery low-power on     # Enable low power mode
    aegis wifi                     # WiFi status
    aegis wifi off                 # Turn off WiFi
    aegis bluetooth on/off         # Toggle Bluetooth
    aegis airplane on/off          # Airplane mode
    aegis location                 # Current GPS
    aegis location history         # Location history
    aegis geofence add <name> <lat> <lon> [radius]
    aegis dnd on/off               # Do Not Disturb
    aegis focus <mode>             # Set Focus mode
    aegis volume <0-100>           # Set volume
    aegis play/pause/next/prev     # Media control
    aegis photo [front|back]       # Take photo
    aegis flashlight on/off        # Flashlight
    aegis storage                  # Storage usage
    aegis steps                    # Today's steps
    aegis info                     # Device info
    aegis brightness <0-100>       # Set brightness
    aegis lock                     # Lock device
    aegis find                     # Play Find My sound
    aegis clipboard                # Get clipboard
    aegis clipboard "text"         # Set clipboard
    aegis run <shortcut>           # Run any shortcut
    aegis shortcuts                # List shortcuts
    aegis status                   # Full status
    aegis setup                    # Setup guide
    aegis report                   # Full report
    aegis init                     # Initialize DB
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from device_ops_department.engine.database import DeviceOpsDB
from device_ops_department.engine.battery import BatteryEngine
from device_ops_department.engine.connectivity import ConnectivityEngine
from device_ops_department.engine.location import LocationEngine
from device_ops_department.engine.notifications import NotificationsEngine
from device_ops_department.engine.media import MediaEngine
from device_ops_department.engine.storage import StorageEngine
from device_ops_department.engine.health import HealthEngine
from device_ops_department.engine.sysinfo import SystemInfoEngine
from device_ops_department.engine.security import SecurityEngine
from device_ops_department.engine.automation import AutomationEngine
from device_ops_department.engine.app_control import AppControlEngine
from device_ops_department.engine.clipboard import ClipboardEngine


class Aegis:
    """AEGIS - Device Operations Director."""

    def __init__(self):
        self.db = DeviceOpsDB()
        self.battery = BatteryEngine(db=self.db)
        self.connectivity = ConnectivityEngine(db=self.db)
        self.location = LocationEngine(db=self.db)
        self.notifications = NotificationsEngine(db=self.db)
        self.media = MediaEngine(db=self.db)
        self.storage = StorageEngine(db=self.db)
        self.health = HealthEngine(db=self.db)
        self.sysinfo = SystemInfoEngine(db=self.db)
        self.security = SecurityEngine(db=self.db)
        self.automation = AutomationEngine(db=self.db)
        self.app_control = AppControlEngine(db=self.db)
        self.clipboard = ClipboardEngine(db=self.db)

    def init(self):
        self.db.init_tables()
        return {"status": "initialized", "tables": [
            "devops_snapshots", "devops_events", "devops_commands",
            "devops_locations", "devops_geofences",
        ]}

    def handle_command(self, args: list) -> dict:
        if not args:
            return self.status()

        cmd = args[0].lower()
        rest = args[1:]

        handlers = {
            # Battery
            "battery": self._cmd_battery,
            "batt": self._cmd_battery,
            # Connectivity
            "wifi": self._cmd_wifi,
            "bluetooth": self._cmd_bluetooth,
            "bt": self._cmd_bluetooth,
            "airplane": self._cmd_toggle("airplane", self.connectivity.toggle_airplane_mode),
            "cellular": lambda _: self.connectivity.get_cellular_status(),
            "vpn": lambda _: self.connectivity.get_vpn_status(),
            "connectivity": lambda _: self.connectivity.get_full_status(),
            # Location
            "location": self._cmd_location,
            "loc": self._cmd_location,
            "gps": lambda _: self.location.get_current(),
            "geofence": self._cmd_geofence,
            # Notifications
            "dnd": self._cmd_toggle("Do Not Disturb", self._set_focus),
            "focus": self._cmd_focus,
            "notify": self._cmd_notify,
            # Media
            "volume": self._cmd_volume,
            "vol": self._cmd_volume,
            "play": lambda _: self.media.toggle_playback("play"),
            "pause": lambda _: self.media.toggle_playback("pause"),
            "next": lambda _: self.media.toggle_playback("next"),
            "prev": lambda _: self.media.toggle_playback("previous"),
            "previous": lambda _: self.media.toggle_playback("previous"),
            "playing": lambda _: self.media.get_now_playing(),
            "photo": self._cmd_photo,
            "flashlight": self._cmd_toggle("flashlight", self.media.set_flashlight),
            "flash": self._cmd_toggle("flashlight", self.media.set_flashlight),
            "sound": lambda _: self.media.play_sound(),
            # Storage
            "storage": lambda _: self.storage.get_usage(),
            "icloud": lambda _: self.storage.get_icloud_status(),
            "files": self._cmd_files,
            # Health
            "steps": lambda _: self.health.get_steps(),
            "screentime": lambda _: self.health.get_screen_time(),
            "motion": lambda _: self.health.get_motion_data(),
            # System Info
            "info": lambda _: self.sysinfo.get_device_info(),
            "brightness": self._cmd_brightness,
            "report": lambda _: self.sysinfo.get_full_report(),
            # Security
            "lock": lambda _: self.security.lock_device(),
            "find": lambda _: self.security.find_my_iphone(),
            "findmy": lambda _: self.security.find_my_iphone(),
            "wipe": self._cmd_wipe,
            # Automation
            "run": self._cmd_run_shortcut,
            "shortcuts": lambda _: self.automation.list_shortcuts(),
            # App Control
            "open": self._cmd_open,
            "app": self._cmd_open,
            "usage": lambda _: self.app_control.get_app_usage(),
            # Clipboard
            "clipboard": self._cmd_clipboard,
            "clip": self._cmd_clipboard,
            "paste": lambda _: self.clipboard.get(),
            "copy": self._cmd_clipboard_set,
            # System
            "status": lambda _: self.status(),
            "setup": lambda _: self._setup_info(),
            "init": lambda _: self.init(),
            "ping": lambda _: self.battery.ping(),
            "events": self._cmd_events,
            "commands": self._cmd_commands,
        }

        handler = handlers.get(cmd)
        if handler:
            return handler(rest)

        return {"error": f"Unknown command: {cmd}. Try: aegis status"}

    # --- Command handlers ---

    def _cmd_battery(self, args: list) -> dict:
        if not args:
            return self.battery.get_status()
        if args[0] == "level":
            return self.battery.get_level()
        if args[0] == "low-power" and len(args) > 1:
            return self.battery.set_low_power_mode(args[1].lower() in ("on", "true", "1"))
        return self.battery.get_status()

    def _cmd_wifi(self, args: list) -> dict:
        if not args:
            return self.connectivity.get_wifi_status()
        return self.connectivity.toggle_wifi(args[0].lower() in ("on", "true", "1"))

    def _cmd_bluetooth(self, args: list) -> dict:
        if not args:
            return self.connectivity.get_bluetooth_status()
        return self.connectivity.toggle_bluetooth(args[0].lower() in ("on", "true", "1"))

    def _cmd_toggle(self, name: str, fn):
        def handler(args):
            if not args:
                return {"error": f"Usage: aegis {name} on|off"}
            return fn(args[0].lower() in ("on", "true", "1"))
        return handler

    def _set_focus(self, enabled: bool) -> dict:
        return self.notifications.set_focus_mode("Do Not Disturb", enabled)

    def _cmd_focus(self, args: list) -> dict:
        if not args:
            return self.notifications.get_focus_mode()
        mode = args[0]
        enabled = True
        if len(args) > 1:
            enabled = args[1].lower() in ("on", "true", "1")
        return self.notifications.set_focus_mode(mode, enabled)

    def _cmd_notify(self, args: list) -> dict:
        if not args:
            return self.notifications.get_notification_summary()
        title = args[0]
        body = " ".join(args[1:]) if len(args) > 1 else ""
        return self.notifications.send_notification(title, body)

    def _cmd_volume(self, args: list) -> dict:
        if not args:
            return self.media.get_volume()
        try:
            return self.media.set_volume(int(args[0]))
        except ValueError:
            return {"error": "Usage: aegis volume <0-100>"}

    def _cmd_photo(self, args: list) -> dict:
        camera = args[0] if args else "back"
        return self.media.take_photo(camera)

    def _cmd_location(self, args: list) -> dict:
        if not args:
            return self.location.get_current()
        if args[0] == "history":
            limit = int(args[1]) if len(args) > 1 else 100
            return {"locations": self.location.get_history(limit=limit)}
        if args[0] == "address":
            return self.location.get_address()
        return self.location.get_current()

    def _cmd_geofence(self, args: list) -> dict:
        if not args or args[0] == "list":
            return {"geofences": self.location.list_geofences()}
        if args[0] == "add" and len(args) >= 4:
            name = args[1]
            lat, lon = float(args[2]), float(args[3])
            radius = float(args[4]) if len(args) > 4 else 100.0
            return self.location.add_geofence(name, lat, lon, radius)
        if args[0] == "delete" and len(args) >= 2:
            return {"deleted": self.location.delete_geofence(int(args[1]))}
        return {"error": "Usage: aegis geofence [list|add <name> <lat> <lon> [radius]|delete <id>]"}

    def _cmd_brightness(self, args: list) -> dict:
        if not args:
            return self.sysinfo.get_screen_brightness()
        try:
            return self.sysinfo.set_screen_brightness(int(args[0]))
        except ValueError:
            return {"error": "Usage: aegis brightness <0-100>"}

    def _cmd_wipe(self, args: list) -> dict:
        if not args or args[0] == "request":
            return self.security.request_wipe()
        if args[0] == "confirm" and len(args) > 1:
            return self.security.confirm_wipe(args[1])
        return {"error": "Usage: aegis wipe request | aegis wipe confirm <token>"}

    def _cmd_run_shortcut(self, args: list) -> dict:
        if not args:
            return {"error": "Usage: aegis run <shortcut_name> [input_json]"}
        name = args[0]
        input_data = None
        if len(args) > 1:
            try:
                input_data = json.loads(" ".join(args[1:]))
            except json.JSONDecodeError:
                input_data = {"input": " ".join(args[1:])}
        return self.automation.run_shortcut(name, input_data)

    def _cmd_open(self, args: list) -> dict:
        if not args:
            return {"error": "Usage: aegis open <app_name>"}
        if "://" in args[0] or "." in args[0]:
            return self.app_control.open_url(args[0])
        return self.app_control.open_app(" ".join(args))

    def _cmd_clipboard(self, args: list) -> dict:
        if not args:
            return self.clipboard.get()
        return self.clipboard.set(" ".join(args))

    def _cmd_clipboard_set(self, args: list) -> dict:
        if not args:
            return {"error": "Usage: aegis copy <text>"}
        return self.clipboard.set(" ".join(args))

    def _cmd_files(self, args: list) -> dict:
        if not args or args[0] == "list":
            folder = args[1] if len(args) > 1 else "AEGIS"
            return self.storage.list_files(folder)
        if args[0] == "read" and len(args) > 1:
            return self.storage.read_file(args[1])
        if args[0] == "save" and len(args) > 2:
            return self.storage.save_file(args[1], " ".join(args[2:]))
        return {"error": "Usage: aegis files [list [folder]|read <path>|save <name> <content>]"}

    def _cmd_events(self, args: list) -> dict:
        event_type = None
        if args:
            event_type = args[0]
        return {"events": self.db.get_events(event_type=event_type)}

    def _cmd_commands(self, args: list) -> dict:
        subsystem = None
        if args:
            subsystem = args[0]
        return {"commands": self.db.get_commands(subsystem=subsystem)}

    def status(self) -> dict:
        bridge = self.battery.ping()
        return {
            "agent": "AEGIS",
            "department": "Device Operations",
            "pushcut": bridge,
            "sub_agents": [
                "AEGIS-BATTERY", "AEGIS-CONNECTIVITY", "AEGIS-LOCATION",
                "AEGIS-NOTIFICATIONS", "AEGIS-MEDIA", "AEGIS-STORAGE",
                "AEGIS-HEALTH", "AEGIS-SYSINFO", "AEGIS-SECURITY",
                "AEGIS-AUTOMATION", "AEGIS-APPCONTROL", "AEGIS-CLIPBOARD",
            ],
        }

    def _setup_info(self) -> dict:
        from device_ops_department.engine.setup_agent import AegisSetupAgent, AEGIS_SHORTCUTS
        agent = AegisSetupAgent()
        return {
            "title": "AEGIS Device Operations Setup",
            "pushcut_status": agent.verify_pushcut(),
            "shortcuts_needed": len(AEGIS_SHORTCUTS),
            "setup_page": f"{agent.webhook_base}/api/device/setup",
            "steps": [
                "1. Ensure Pushcut Automation Server is running on iPhone",
                "2. Open the setup page URL on your iPhone",
                "3. Install all AEGIS shortcuts (tap each install button)",
                "4. Test: aegis battery",
            ],
        }


def main():
    aegis = Aegis()
    if len(sys.argv) < 2:
        result = aegis.status()
    else:
        result = aegis.handle_command(sys.argv[1:])
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
