"""AEGIS Device Operations API - FastAPI endpoints.

Run: uvicorn device_ops_department.api.server:app --host 0.0.0.0 --port 3200
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, Response
from pydantic import BaseModel
from typing import Optional

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
from device_ops_department.engine.setup_agent import AegisSetupAgent

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aegis.api")

app = FastAPI(
    title="AEGIS Device Operations API",
    description="Carbon6 Device Operations Department - iPhone control via Pushcut + Shortcuts",
    version="1.0.0",
)

# Initialize
db = DeviceOpsDB()
battery = BatteryEngine(db=db)
connectivity = ConnectivityEngine(db=db)
location = LocationEngine(db=db)
notifications = NotificationsEngine(db=db)
media = MediaEngine(db=db)
storage = StorageEngine(db=db)
health = HealthEngine(db=db)
sysinfo = SystemInfoEngine(db=db)
security = SecurityEngine(db=db)
automation = AutomationEngine(db=db)
app_control = AppControlEngine(db=db)
clipboard = ClipboardEngine(db=db)
setup_agent = AegisSetupAgent()


# --- Pydantic models ---

class ToggleRequest(BaseModel):
    enabled: bool

class VolumeSet(BaseModel):
    level: int

class BrightnessSet(BaseModel):
    level: int

class FocusMode(BaseModel):
    mode: str
    enabled: bool

class ClipboardSet(BaseModel):
    content: str

class ShortcutRun(BaseModel):
    name: str
    input: Optional[dict] = None

class GeofenceCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    radius_meters: float = 100.0
    on_enter_action: Optional[dict] = None
    on_exit_action: Optional[dict] = None

class FileSave(BaseModel):
    name: str
    content: str
    folder: str = "AEGIS"

class NotificationSend(BaseModel):
    title: str
    body: str = ""

class AppOpen(BaseModel):
    app_name: str

class UrlOpen(BaseModel):
    url: str

class MediaControl(BaseModel):
    action: str = "playpause"

class PhotoRequest(BaseModel):
    camera: str = "back"

class WipeConfirm(BaseModel):
    token: str

class WebhookEvent(BaseModel):
    event_type: str
    data: Optional[dict] = {}
    severity: str = "info"


# --- Battery ---

@app.get("/api/device/battery")
async def get_battery():
    return battery.get_status()

@app.get("/api/device/battery/level")
async def get_battery_level():
    return battery.get_level()

@app.post("/api/device/battery/low-power")
async def set_low_power(req: ToggleRequest):
    return battery.set_low_power_mode(req.enabled)


# --- Connectivity ---

@app.get("/api/device/connectivity")
async def get_connectivity():
    return connectivity.get_full_status()

@app.get("/api/device/connectivity/wifi")
async def get_wifi():
    return connectivity.get_wifi_status()

@app.post("/api/device/connectivity/wifi")
async def set_wifi(req: ToggleRequest):
    return connectivity.toggle_wifi(req.enabled)

@app.get("/api/device/connectivity/bluetooth")
async def get_bluetooth():
    return connectivity.get_bluetooth_status()

@app.post("/api/device/connectivity/bluetooth")
async def set_bluetooth(req: ToggleRequest):
    return connectivity.toggle_bluetooth(req.enabled)

@app.post("/api/device/connectivity/airplane")
async def set_airplane(req: ToggleRequest):
    return connectivity.toggle_airplane_mode(req.enabled)

@app.get("/api/device/connectivity/vpn")
async def get_vpn():
    return connectivity.get_vpn_status()


# --- Location ---

@app.get("/api/device/location")
async def get_location():
    return location.get_current()

@app.get("/api/device/location/address")
async def get_address():
    return location.get_address()

@app.get("/api/device/location/history")
async def get_location_history(limit: int = 100):
    return location.get_history(limit=limit)

@app.get("/api/device/location/geofences")
async def get_geofences():
    return location.list_geofences()

@app.post("/api/device/location/geofences")
async def create_geofence(gf: GeofenceCreate):
    return location.add_geofence(
        gf.name, gf.latitude, gf.longitude, gf.radius_meters,
        on_enter=gf.on_enter_action, on_exit=gf.on_exit_action,
    )

@app.delete("/api/device/location/geofences/{geofence_id}")
async def remove_geofence(geofence_id: int):
    if location.delete_geofence(geofence_id):
        return {"deleted": geofence_id}
    raise HTTPException(404, "Geofence not found")


# --- Notifications ---

@app.get("/api/device/notifications/focus")
async def get_focus():
    return notifications.get_focus_mode()

@app.post("/api/device/notifications/focus")
async def set_focus(req: FocusMode):
    return notifications.set_focus_mode(req.mode, req.enabled)

@app.post("/api/device/notifications/send")
async def send_notification(req: NotificationSend):
    return notifications.send_notification(req.title, req.body)

@app.get("/api/device/notifications/summary")
async def notification_summary():
    return notifications.get_notification_summary()


# --- Media ---

@app.get("/api/device/media/volume")
async def get_volume():
    return media.get_volume()

@app.post("/api/device/media/volume")
async def set_volume(req: VolumeSet):
    return media.set_volume(req.level)

@app.post("/api/device/media/playback")
async def media_playback(req: MediaControl):
    return media.toggle_playback(req.action)

@app.get("/api/device/media/now-playing")
async def now_playing():
    return media.get_now_playing()

@app.post("/api/device/media/photo")
async def take_photo(req: PhotoRequest):
    return media.take_photo(req.camera)

@app.post("/api/device/media/flashlight")
async def set_flashlight(req: ToggleRequest):
    return media.set_flashlight(req.enabled)

@app.post("/api/device/media/sound")
async def play_sound():
    return media.play_sound()


# --- Storage ---

@app.get("/api/device/storage")
async def get_storage():
    return storage.get_usage()

@app.get("/api/device/storage/icloud")
async def get_icloud():
    return storage.get_icloud_status()

@app.get("/api/device/storage/files")
async def list_files(folder: str = "AEGIS"):
    return storage.list_files(folder)

@app.post("/api/device/storage/files")
async def save_file(req: FileSave):
    return storage.save_file(req.name, req.content, req.folder)


# --- Health ---

@app.get("/api/device/health/steps")
async def get_steps(date: str = "today"):
    return health.get_steps(date)

@app.get("/api/device/health/screentime")
async def get_screen_time():
    return health.get_screen_time()

@app.get("/api/device/health/motion")
async def get_motion():
    return health.get_motion_data()


# --- System Info ---

@app.get("/api/device/sysinfo")
async def get_sysinfo():
    return sysinfo.get_device_info()

@app.get("/api/device/sysinfo/brightness")
async def get_brightness():
    return sysinfo.get_screen_brightness()

@app.post("/api/device/sysinfo/brightness")
async def set_brightness(req: BrightnessSet):
    return sysinfo.set_screen_brightness(req.level)

@app.get("/api/device/sysinfo/report")
async def device_report():
    return sysinfo.get_full_report()


# --- Security ---

@app.post("/api/device/security/lock")
async def lock_device():
    return security.lock_device()

@app.post("/api/device/security/find")
async def find_device():
    return security.find_my_iphone()

@app.get("/api/device/security/status")
async def security_status():
    return security.get_security_status()

@app.post("/api/device/security/wipe/request")
async def request_wipe():
    return security.request_wipe()

@app.post("/api/device/security/wipe/confirm")
async def confirm_wipe(req: WipeConfirm):
    return security.confirm_wipe(req.token)


# --- Automation ---

@app.get("/api/device/automation/shortcuts")
async def list_shortcuts():
    return automation.list_shortcuts()

@app.post("/api/device/automation/run")
async def run_shortcut(req: ShortcutRun):
    return automation.run_shortcut(req.name, req.input)


# --- App Control ---

@app.post("/api/device/apps/open")
async def open_app(req: AppOpen):
    return app_control.open_app(req.app_name)

@app.get("/api/device/apps/usage")
async def app_usage():
    return app_control.get_app_usage()

@app.post("/api/device/apps/url")
async def open_url(req: UrlOpen):
    return app_control.open_url(req.url)


# --- Clipboard ---

@app.get("/api/device/clipboard")
async def get_clipboard():
    return clipboard.get()

@app.post("/api/device/clipboard")
async def set_clipboard(req: ClipboardSet):
    return clipboard.set(req.content)


# --- Webhook (inbound from iPhone) ---

@app.post("/api/device/webhook/event")
async def webhook_event(evt: WebhookEvent):
    """Universal inbound webhook - iPhone automations POST events here."""
    event_id = db.store_event(evt.event_type, severity=evt.severity, data=evt.data)
    log.info(f"Inbound event: {evt.event_type} (severity={evt.severity})")
    return {"received": True, "event_id": event_id}


# --- Events & Commands ---

@app.get("/api/device/events")
async def get_events(event_type: Optional[str] = None, severity: Optional[str] = None,
                     unacknowledged: bool = False, limit: int = 50):
    return db.get_events(event_type=event_type, severity=severity,
                         unacknowledged=unacknowledged, limit=limit)

@app.post("/api/device/events/{event_id}/ack")
async def ack_event(event_id: int):
    if db.acknowledge_event(event_id):
        return {"acknowledged": event_id}
    raise HTTPException(404, "Event not found")

@app.get("/api/device/commands")
async def get_commands(subsystem: Optional[str] = None, limit: int = 50):
    return db.get_commands(subsystem=subsystem, limit=limit)

@app.get("/api/device/snapshots")
async def get_snapshots(snapshot_type: Optional[str] = None, limit: int = 50):
    return db.get_snapshots(snapshot_type=snapshot_type, limit=limit)


# --- Setup ---

@app.get("/api/device/setup", response_class=HTMLResponse)
async def setup_page():
    return setup_agent.generate_setup_page_html()

@app.post("/api/device/setup/run")
async def run_setup():
    return setup_agent.run_full_setup()

@app.get("/api/device/setup/shortcut/{name}")
async def download_shortcut(name: str):
    data = setup_agent.generate_shortcut_file(name)
    if not data:
        raise HTTPException(404, f"Shortcut '{name}' not found")
    return Response(
        content=data,
        media_type="application/x-apple-shortcut",
        headers={"Content-Disposition": f'attachment; filename="AEGIS {name}.shortcut"'},
    )

@app.get("/api/device/setup/verify")
async def verify_setup():
    return setup_agent.verify_pushcut()


# --- Status ---

@app.get("/api/device/status")
async def status():
    bridge_status = battery.ping()
    return {
        "agent": "AEGIS",
        "department": "Device Operations",
        "pushcut": bridge_status,
        "subsystems": {
            "battery": "active",
            "connectivity": "active",
            "location": "active",
            "notifications": "active",
            "media": "active",
            "storage": "active",
            "health": "active",
            "sysinfo": "active",
            "security": "active",
            "automation": "active",
            "appcontrol": "active",
            "clipboard": "active",
        },
        "queues": {
            "battery": battery.queue_size(),
            "connectivity": connectivity.queue_size(),
            "location": location.queue_size(),
            "media": media.queue_size(),
            "security": security.queue_size(),
        },
    }


@app.post("/api/device/init")
async def init_db():
    db.init_tables()
    return {"status": "initialized"}
