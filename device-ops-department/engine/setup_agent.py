"""AEGIS Setup Agent - Generate Apple Shortcuts and serve setup page.

Generates all AEGIS shortcut files for iPhone installation.
Each shortcut maps to a device operation triggered via Pushcut.
"""
import logging
import os
import plistlib
import urllib.parse

import requests

from ..config.settings import load_config

log = logging.getLogger("aegis.setup")

PUSHCUT_API = "https://api.pushcut.io"

# All AEGIS shortcuts and what they do
AEGIS_SHORTCUTS = {
    # Battery
    "Get Battery Status": {
        "subsystem": "battery",
        "description": "Returns battery level, charging state, low power mode",
        "actions": ["get_battery_level", "get_device_detail:IsCharging", "get_low_power_mode", "build_dict", "return"],
        "icon_color": 4282601983,  # Green
        "icon_glyph": 59778,  # Battery
    },
    "Get Battery Level": {
        "subsystem": "battery",
        "description": "Returns battery percentage as number",
        "actions": ["get_battery_level", "return"],
        "icon_color": 4282601983,
        "icon_glyph": 59778,
    },
    "Set Low Power Mode": {
        "subsystem": "battery",
        "description": "Toggle low power mode on/off",
        "actions": ["parse_input", "set_low_power_mode", "return"],
        "icon_color": 4282601983,
        "icon_glyph": 59778,
    },
    # Connectivity
    "Get WiFi Status": {
        "subsystem": "connectivity",
        "description": "Returns current WiFi network name and IP",
        "actions": ["get_wifi_network", "get_ip_address", "build_dict", "return"],
        "icon_color": 463140863,  # Blue
        "icon_glyph": 59735,  # WiFi
    },
    "Set WiFi": {
        "subsystem": "connectivity",
        "description": "Toggle WiFi on/off",
        "actions": ["parse_input", "set_wifi", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59735,
    },
    "Get Bluetooth": {
        "subsystem": "connectivity",
        "description": "Get Bluetooth state",
        "actions": ["get_bluetooth", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59680,
    },
    "Set Bluetooth": {
        "subsystem": "connectivity",
        "description": "Toggle Bluetooth on/off",
        "actions": ["parse_input", "set_bluetooth", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59680,
    },
    "Set Airplane Mode": {
        "subsystem": "connectivity",
        "description": "Toggle Airplane Mode",
        "actions": ["parse_input", "set_airplane_mode", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59180,
    },
    "Get Connectivity": {
        "subsystem": "connectivity",
        "description": "Full connectivity snapshot",
        "actions": ["get_wifi_network", "get_bluetooth", "get_cellular", "build_dict", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59735,
    },
    # Location
    "Get Location": {
        "subsystem": "location",
        "description": "Get GPS coordinates and address",
        "actions": ["get_current_location", "reverse_geocode", "build_dict", "return"],
        "icon_color": 4251333119,  # Red
        "icon_glyph": 59507,  # Pin
    },
    # Notifications
    "Get Focus Mode": {
        "subsystem": "notifications",
        "description": "Get current Focus/DND status",
        "actions": ["get_focus_mode", "return"],
        "icon_color": 2071128575,  # Purple
        "icon_glyph": 59198,  # Moon
    },
    "Set Focus Mode": {
        "subsystem": "notifications",
        "description": "Enable/disable a Focus mode",
        "actions": ["parse_input", "set_focus_mode", "return"],
        "icon_color": 2071128575,
        "icon_glyph": 59198,
    },
    # Media
    "Set Volume": {
        "subsystem": "media",
        "description": "Set device volume (0-100)",
        "actions": ["parse_input", "set_volume", "return"],
        "icon_color": 4271458559,  # Orange
        "icon_glyph": 59316,  # Speaker
    },
    "Get Volume": {
        "subsystem": "media",
        "description": "Get current volume level",
        "actions": ["get_volume", "return"],
        "icon_color": 4271458559,
        "icon_glyph": 59316,
    },
    "Media Control": {
        "subsystem": "media",
        "description": "Play/pause/next/previous",
        "actions": ["parse_input", "media_control", "return"],
        "icon_color": 4271458559,
        "icon_glyph": 59316,
    },
    "Get Now Playing": {
        "subsystem": "media",
        "description": "Get current media info",
        "actions": ["get_now_playing", "return"],
        "icon_color": 4271458559,
        "icon_glyph": 59316,
    },
    "Take Photo": {
        "subsystem": "media",
        "description": "Take photo with front/back camera",
        "actions": ["parse_input", "take_photo", "return"],
        "icon_color": 4271458559,
        "icon_glyph": 59473,  # Camera
    },
    "Set Flashlight": {
        "subsystem": "media",
        "description": "Toggle flashlight on/off",
        "actions": ["parse_input", "set_flashlight", "return"],
        "icon_color": 4271458559,
        "icon_glyph": 59694,
    },
    # Storage
    "Get Storage": {
        "subsystem": "storage",
        "description": "Get disk space used/free",
        "actions": ["get_device_detail:DiskSpace", "build_dict", "return"],
        "icon_color": 1440408063,  # Teal
        "icon_glyph": 59442,  # Folder
    },
    # Health
    "Get Steps": {
        "subsystem": "health",
        "description": "Get step count for today",
        "actions": ["find_health_samples:steps", "return"],
        "icon_color": 4282601983,
        "icon_glyph": 59369,  # Heart
    },
    "Get Screen Time": {
        "subsystem": "health",
        "description": "Get screen time data",
        "actions": ["get_screen_time", "return"],
        "icon_color": 4282601983,
        "icon_glyph": 59369,
    },
    # System Info
    "Get Device Info": {
        "subsystem": "sysinfo",
        "description": "Device model, OS version, name",
        "actions": ["get_device_detail:Name", "get_device_detail:Model", "get_device_detail:SystemVersion", "build_dict", "return"],
        "icon_color": 3679049983,  # Gray
        "icon_glyph": 59461,  # Gear
    },
    "Get Brightness": {
        "subsystem": "sysinfo",
        "description": "Get screen brightness",
        "actions": ["get_brightness", "return"],
        "icon_color": 3679049983,
        "icon_glyph": 59461,
    },
    "Set Brightness": {
        "subsystem": "sysinfo",
        "description": "Set screen brightness (0-100)",
        "actions": ["parse_input", "set_brightness", "return"],
        "icon_color": 3679049983,
        "icon_glyph": 59461,
    },
    "Device Report": {
        "subsystem": "sysinfo",
        "description": "Full device report",
        "actions": ["get_all_device_details", "get_battery_level", "build_dict", "return"],
        "icon_color": 3679049983,
        "icon_glyph": 59461,
    },
    # Security
    "Lock Device": {
        "subsystem": "security",
        "description": "Lock the screen",
        "actions": ["lock_screen", "return"],
        "icon_color": 4251333119,
        "icon_glyph": 59493,  # Lock
    },
    "Find My Sound": {
        "subsystem": "security",
        "description": "Play Find My iPhone sound",
        "actions": ["play_sound", "return"],
        "icon_color": 4251333119,
        "icon_glyph": 59493,
    },
    # Automation
    "List Shortcuts": {
        "subsystem": "automation",
        "description": "List all shortcuts on device",
        "actions": ["get_my_shortcuts", "return"],
        "icon_color": 463140863,
        "icon_glyph": 59758,
    },
    # App Control
    "Open App": {
        "subsystem": "appcontrol",
        "description": "Open an app by name",
        "actions": ["parse_input", "open_app", "return"],
        "icon_color": 1440408063,
        "icon_glyph": 59508,
    },
    "Open URL": {
        "subsystem": "appcontrol",
        "description": "Open a URL on device",
        "actions": ["parse_input", "open_url", "return"],
        "icon_color": 1440408063,
        "icon_glyph": 59508,
    },
    # Clipboard
    "Get Clipboard": {
        "subsystem": "clipboard",
        "description": "Get clipboard content",
        "actions": ["get_clipboard", "return"],
        "icon_color": 3679049983,
        "icon_glyph": 59541,
    },
    "Set Clipboard": {
        "subsystem": "clipboard",
        "description": "Set clipboard content",
        "actions": ["parse_input", "copy_to_clipboard", "return"],
        "icon_color": 3679049983,
        "icon_glyph": 59541,
    },
}


class AegisSetupAgent:
    """Automated setup for all AEGIS device shortcuts."""

    def __init__(self):
        self.config = load_config()
        self.api_key = self.config.pushcut.api_key
        self.device_name = self.config.pushcut.device_name
        self.webhook_base = self.config.webhook_base

    def verify_pushcut(self) -> dict:
        if not self.api_key:
            return {"ok": False, "error": "PUSHCUT_API_KEY not set"}
        try:
            resp = requests.post(
                f"{PUSHCUT_API}/{self.api_key}/execute",
                params={"shortcut": "__ping__", "timeout": "nowait"},
                timeout=10,
            )
            if resp.status_code in (200, 202):
                return {"ok": True, "detail": "Pushcut Automation Server is reachable"}
            if "Invalid secret" in resp.text:
                return {"ok": False, "error": "Invalid Pushcut API key"}
            return {"ok": True, "detail": f"Pushcut responded ({resp.status_code})"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def generate_shortcut_file(self, name: str) -> bytes:
        """Generate a .shortcut plist file for a given AEGIS shortcut."""
        info = AEGIS_SHORTCUTS.get(name)
        if not info:
            return None

        shortcut = {
            "WFWorkflowMinimumClientVersionString": "900",
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowIcon": {
                "WFWorkflowIconStartColor": info["icon_color"],
                "WFWorkflowIconGlyphNumber": info["icon_glyph"],
            },
            "WFWorkflowClientVersion": "2612.0.4",
            "WFWorkflowOutputContentItemClasses": [],
            "WFWorkflowHasOutputFallback": False,
            "WFWorkflowActions": self._build_actions(name, info),
            "WFWorkflowImportQuestions": [],
            "WFWorkflowTypes": ["ActionExtension"],
            "WFWorkflowInputContentItemClasses": [
                "WFStringContentItem",
                "WFDictionaryContentItem",
            ],
        }
        return plistlib.dumps(shortcut, fmt=plistlib.FMT_BINARY)

    def _build_actions(self, name: str, info: dict) -> list:
        """Build Shortcuts action plist based on the shortcut spec."""
        actions = []

        # Most shortcuts start by parsing JSON input from Pushcut
        if "parse_input" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.detect.dictionary",
                "WFWorkflowActionParameters": {
                    "WFInput": {
                        "Value": {"Type": "ExtensionInput"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-INPUT-0001",
                },
            })

        # Add main action based on shortcut type
        if "get_battery_level" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getbatterylevel",
                "WFWorkflowActionParameters": {"UUID": "AEGIS-BATT-0001"},
            })

        if "get_current_location" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getcurrentlocation",
                "WFWorkflowActionParameters": {"UUID": "AEGIS-LOC-0001"},
            })

        if "get_clipboard" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getclipboard",
                "WFWorkflowActionParameters": {"UUID": "AEGIS-CLIP-0001"},
            })

        if "copy_to_clipboard" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                "WFWorkflowActionParameters": {
                    "WFDictionaryKey": "content",
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-INPUT-0001", "Type": "ActionOutput", "OutputName": "Dictionary"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-CLIP-VAL-0001",
                },
            })
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.setclipboard",
                "WFWorkflowActionParameters": {
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-CLIP-VAL-0001", "Type": "ActionOutput", "OutputName": "Dictionary Value"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            })

        if "set_volume" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                "WFWorkflowActionParameters": {
                    "WFDictionaryKey": "level",
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-INPUT-0001", "Type": "ActionOutput", "OutputName": "Dictionary"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-VOL-VAL-0001",
                },
            })
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.setvolume",
                "WFWorkflowActionParameters": {
                    "WFVolume": {
                        "Value": {"OutputUUID": "AEGIS-VOL-VAL-0001", "Type": "ActionOutput", "OutputName": "Dictionary Value"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            })

        if "set_brightness" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                "WFWorkflowActionParameters": {
                    "WFDictionaryKey": "level",
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-INPUT-0001", "Type": "ActionOutput", "OutputName": "Dictionary"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-BRT-VAL-0001",
                },
            })
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.setbrightness",
                "WFWorkflowActionParameters": {
                    "WFBrightness": {
                        "Value": {"OutputUUID": "AEGIS-BRT-VAL-0001", "Type": "ActionOutput", "OutputName": "Dictionary Value"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            })

        if "open_app" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                "WFWorkflowActionParameters": {
                    "WFDictionaryKey": "app",
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-INPUT-0001", "Type": "ActionOutput", "OutputName": "Dictionary"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-APP-VAL-0001",
                },
            })
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.openapp",
                "WFWorkflowActionParameters": {
                    "WFAppIdentifier": {
                        "Value": {"OutputUUID": "AEGIS-APP-VAL-0001", "Type": "ActionOutput", "OutputName": "Dictionary Value"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            })

        if "open_url" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.getvalueforkey",
                "WFWorkflowActionParameters": {
                    "WFDictionaryKey": "url",
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-INPUT-0001", "Type": "ActionOutput", "OutputName": "Dictionary"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                    "UUID": "AEGIS-URL-VAL-0001",
                },
            })
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.openurl",
                "WFWorkflowActionParameters": {
                    "WFInput": {
                        "Value": {"OutputUUID": "AEGIS-URL-VAL-0001", "Type": "ActionOutput", "OutputName": "Dictionary Value"},
                        "WFSerializationType": "WFTextTokenAttachment",
                    },
                },
            })

        if "take_photo" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.takephoto",
                "WFWorkflowActionParameters": {"UUID": "AEGIS-PHOTO-0001"},
            })

        if "play_sound" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.playsound",
                "WFWorkflowActionParameters": {},
            })

        if "lock_screen" in info["actions"]:
            actions.append({
                "WFWorkflowActionIdentifier": "is.workflow.actions.lockscreen",
                "WFWorkflowActionParameters": {},
            })

        # For device detail queries
        for action in info["actions"]:
            if action.startswith("get_device_detail:"):
                detail = action.split(":")[1]
                actions.append({
                    "WFWorkflowActionIdentifier": "is.workflow.actions.getdevicedetails",
                    "WFWorkflowActionParameters": {
                        "WFDeviceDetail": detail,
                        "UUID": f"AEGIS-DEV-{detail}",
                    },
                })

        return actions

    def run_full_setup(self) -> dict:
        results = {"steps": [], "success": True}

        # Verify Pushcut
        pushcut_status = self.verify_pushcut()
        results["steps"].append({
            "step": 1, "name": "Verify Pushcut",
            "status": "ok" if pushcut_status.get("ok") else "failed",
            "detail": pushcut_status,
        })
        if not pushcut_status.get("ok"):
            results["success"] = False

        # List all shortcuts to generate
        results["steps"].append({
            "step": 2, "name": "Shortcuts Ready",
            "status": "ok",
            "detail": {
                "total_shortcuts": len(AEGIS_SHORTCUTS),
                "by_subsystem": {},
            },
        })
        for name, info in AEGIS_SHORTCUTS.items():
            sub = info["subsystem"]
            results["steps"][-1]["detail"]["by_subsystem"].setdefault(sub, []).append(name)

        # Generate install URLs
        api_base = self.webhook_base
        results["install"] = {
            "setup_page": f"{api_base}/api/device/setup",
            "shortcuts": {
                name: f"{api_base}/api/device/setup/shortcut/{urllib.parse.quote(name)}"
                for name in AEGIS_SHORTCUTS
            },
        }

        return results

    def generate_setup_page_html(self) -> str:
        api_base = self.webhook_base

        # Group shortcuts by subsystem
        by_subsystem = {}
        for name, info in AEGIS_SHORTCUTS.items():
            by_subsystem.setdefault(info["subsystem"], []).append((name, info))

        subsystem_labels = {
            "battery": ("Battery & Power", "59778"),
            "connectivity": ("Connectivity", "59735"),
            "location": ("Location & GPS", "59507"),
            "notifications": ("Notifications & Focus", "59198"),
            "media": ("Media & Audio", "59316"),
            "storage": ("Storage & Files", "59442"),
            "health": ("Health & Activity", "59369"),
            "sysinfo": ("System Info", "59461"),
            "security": ("Security", "59493"),
            "automation": ("Automation", "59758"),
            "appcontrol": ("App Control", "59508"),
            "clipboard": ("Clipboard", "59541"),
        }

        cards_html = ""
        for subsystem, shortcuts in by_subsystem.items():
            label, _ = subsystem_labels.get(subsystem, (subsystem.title(), "59461"))
            buttons = ""
            for name, info in shortcuts:
                file_url = f"{api_base}/api/device/setup/shortcut/{urllib.parse.quote(name)}"
                import_url = f"shortcuts://import-shortcut?url={urllib.parse.quote(file_url, safe='')}&name={urllib.parse.quote(f'AEGIS {name}', safe='')}"
                buttons += f'<a href="{import_url}" class="btn btn-sm">Install "{name}"</a>\n'
                buttons += f'<p class="desc">{info["description"]}</p>\n'

            cards_html += f"""
<div class="card">
  <h2>{label}</h2>
  {buttons}
</div>
"""

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AEGIS Setup</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #000; color: #fff; padding: 20px; }}
  .logo {{ text-align: center; padding: 30px 0 10px; }}
  .logo h1 {{ font-size: 32px; letter-spacing: 4px; }}
  .logo p {{ color: #888; font-size: 13px; margin-top: 5px; }}
  .card {{ background: #1c1c1e; border-radius: 16px; padding: 16px; margin: 12px 0; }}
  .card h2 {{ font-size: 17px; margin-bottom: 10px; color: #0a84ff; }}
  .btn {{ display: block; width: 100%; padding: 12px; border-radius: 10px; border: none;
          font-size: 15px; font-weight: 600; text-align: center; text-decoration: none;
          margin: 6px 0 2px; cursor: pointer; background: #2c2c2e; color: #0a84ff; }}
  .btn-sm {{ font-size: 14px; padding: 10px; }}
  .desc {{ font-size: 12px; color: #666; margin: 0 0 8px; padding-left: 4px; }}
  .status {{ text-align: center; margin: 20px 0; }}
  .status button {{ padding: 14px 28px; border-radius: 12px; border: 2px solid #30d158;
                    background: transparent; color: #30d158; font-size: 16px; font-weight: 600; cursor: pointer; }}
  .small {{ font-size: 11px; color: #444; text-align: center; margin-top: 20px; }}
</style>
</head>
<body>

<div class="logo">
  <h1>AEGIS</h1>
  <p>Advanced Electronics Guardian & Intelligence System</p>
  <p style="color:#555; font-size:11px; margin-top:3px;">{len(AEGIS_SHORTCUTS)} shortcuts &middot; 12 subsystems</p>
</div>

{cards_html}

<div class="status">
  <button onclick="verify()">Verify Connection</button>
  <div id="result" style="margin-top:10px; font-size:14px;"></div>
</div>

<p class="small">AEGIS // Carbon6 Device Operations Department<br>{api_base}</p>

<script>
function verify() {{
  const r = document.getElementById('result');
  r.innerHTML = '<span style="color:#ff9f0a">Testing...</span>';
  fetch('{api_base}/api/device/setup/verify')
    .then(resp => resp.json())
    .then(data => {{
      r.innerHTML = data.ok
        ? '<span style="color:#30d158">Connected to Pushcut!</span>'
        : '<span style="color:#ff453a">' + (data.error || 'Failed') + '</span>';
    }})
    .catch(err => {{
      r.innerHTML = '<span style="color:#ff453a">' + err.message + '</span>';
    }});
}}
</script>

</body>
</html>"""
