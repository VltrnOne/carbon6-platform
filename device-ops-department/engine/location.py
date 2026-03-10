"""AEGIS-LOCATION - GPS tracking, address lookup, and geofencing."""
import logging
import math
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.location")


class LocationEngine(PushcutBridge):
    """Track device location and manage geofences."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="location")

    def get_current(self) -> dict:
        """Get current GPS coordinates and address."""
        result = self.execute_shortcut("AEGIS Get Location")
        if "error" not in result and self.db:
            lat = result.get("latitude")
            lon = result.get("longitude")
            if lat is not None and lon is not None:
                self.db.store_location(
                    latitude=lat, longitude=lon,
                    altitude=result.get("altitude"),
                    address=result.get("address"),
                    accuracy=result.get("accuracy"),
                )
                self._check_geofences(lat, lon)
        return result

    def get_address(self) -> dict:
        """Get reverse-geocoded address string."""
        result = self.get_current()
        return {"address": result.get("address", "Unknown"), **result}

    def get_history(self, limit: int = 100) -> list:
        """Get location history from DB."""
        if self.db:
            return self.db.get_location_history(limit=limit)
        return []

    def add_geofence(self, name: str, latitude: float, longitude: float,
                     radius_meters: float = 100.0,
                     on_enter: dict = None, on_exit: dict = None) -> dict:
        if self.db:
            return self.db.add_geofence(name, latitude, longitude, radius_meters,
                                        on_enter=on_enter, on_exit=on_exit)
        return {"error": "No database configured"}

    def list_geofences(self) -> list:
        if self.db:
            return self.db.list_geofences()
        return []

    def delete_geofence(self, geofence_id: int) -> bool:
        if self.db:
            return self.db.delete_geofence(geofence_id)
        return False

    def _check_geofences(self, lat: float, lon: float):
        """Check current position against all active geofences."""
        if not self.db:
            return

        for gf in self.db.list_geofences():
            distance = self._haversine(lat, lon, gf["latitude"], gf["longitude"])
            inside = distance <= gf["radius_meters"]

            # Store geofence check as event
            if inside:
                self.db.store_event(
                    "geofence_inside", severity="info",
                    data={"geofence": gf["name"], "distance_m": round(distance, 1)},
                )

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in meters between two GPS coordinates."""
        R = 6371000  # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
