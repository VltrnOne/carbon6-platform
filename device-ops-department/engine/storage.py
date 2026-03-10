"""AEGIS-STORAGE - Storage usage, iCloud, and file operations."""
import logging
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.storage")


class StorageEngine(PushcutBridge):
    """Monitor storage and perform file operations via iCloud."""

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="storage")

    def get_usage(self) -> dict:
        """Get disk space used/free."""
        result = self.execute_shortcut("AEGIS Get Storage")
        if "error" not in result and self.db:
            self.db.store_snapshot("storage", result)
            free_gb = result.get("free_gb")
            if free_gb is not None and free_gb <= self.config.monitor.storage_alert_threshold_gb:
                self.db.store_event("storage_low", severity="warning",
                                    data={"free_gb": free_gb})
        return result

    def get_icloud_status(self) -> dict:
        """Check iCloud availability and storage."""
        return self.execute_shortcut("AEGIS Get iCloud Status")

    def save_file(self, name: str, content: str, folder: str = "AEGIS") -> dict:
        """Save a file to iCloud Drive."""
        return self.execute_shortcut("AEGIS Save File",
                                     {"name": name, "content": content, "folder": folder})

    def read_file(self, path: str) -> dict:
        """Read a file from iCloud Drive."""
        return self.execute_shortcut("AEGIS Read File", {"path": path})

    def list_files(self, folder: str = "AEGIS") -> dict:
        """List files in an iCloud Drive folder."""
        return self.execute_shortcut("AEGIS List Files", {"folder": folder})
