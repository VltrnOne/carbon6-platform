"""AEGIS-SECURITY - Lock, Find My, emergency wipe (L4-SECRET clearance)."""
import logging
import secrets
import time
from .pushcut_bridge import PushcutBridge

log = logging.getLogger("aegis.security")


class SecurityEngine(PushcutBridge):
    """Remote security operations - lock, find, wipe with safeguards."""

    WIPE_TOKEN_TTL = 60  # seconds

    def __init__(self, db=None):
        super().__init__(db=db, subsystem="security")

    def lock_device(self) -> dict:
        """Lock the device screen immediately."""
        result = self.execute_shortcut("AEGIS Lock Device")
        if self.db:
            self.db.store_event("device_locked", severity="info")
        return result

    def find_my_iphone(self) -> dict:
        """Play Find My iPhone sound."""
        result = self.execute_shortcut("AEGIS Find My Sound")
        if self.db:
            self.db.store_event("find_my_triggered", severity="info")
        return result

    def get_security_status(self) -> dict:
        """Check passcode/FaceID status."""
        return self.execute_shortcut("AEGIS Get Security Status")

    def request_wipe(self) -> dict:
        """Request emergency wipe - returns a confirmation token.

        Two-step process to prevent accidental remote wipes:
        1. Call request_wipe() -> get a token (valid 60 seconds)
        2. Call confirm_wipe(token) -> executes the wipe
        """
        if not self.redis:
            return {"error": "Redis required for wipe confirmation flow"}

        token = secrets.token_urlsafe(32)
        self.redis.setex(f"{self.config.redis.prefix}wipe_token", self.WIPE_TOKEN_TTL, token)

        if self.db:
            self.db.store_event("wipe_requested", severity="critical",
                                data={"token_expires_in": self.WIPE_TOKEN_TTL})

        log.warning("EMERGENCY WIPE REQUESTED - token issued, expires in 60s")
        return {
            "status": "confirmation_required",
            "token": token,
            "expires_in": self.WIPE_TOKEN_TTL,
            "warning": "Call confirm_wipe with this token within 60 seconds to execute. THIS IS IRREVERSIBLE.",
        }

    def confirm_wipe(self, token: str) -> dict:
        """Confirm emergency wipe with token from request_wipe()."""
        if not self.redis:
            return {"error": "Redis required for wipe confirmation flow"}

        stored_token = self.redis.get(f"{self.config.redis.prefix}wipe_token")
        if not stored_token:
            return {"error": "No pending wipe request or token expired"}
        if stored_token != token:
            return {"error": "Invalid token"}

        # Delete token so it can't be reused
        self.redis.delete(f"{self.config.redis.prefix}wipe_token")

        if self.db:
            self.db.store_event("wipe_confirmed", severity="critical")

        log.critical("EMERGENCY WIPE CONFIRMED - executing")
        return self.execute_shortcut("AEGIS Emergency Wipe")
