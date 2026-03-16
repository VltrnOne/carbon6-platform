"""SENTINEL-VAULT: Encrypted vault management and secret rotation.

Manages:
- AES-256-GCM encrypted secrets vault
- Secret rotation scheduling and execution
- Vault integrity verification
- Rotation audit trail
"""
import base64
import json
import os
import time
from datetime import datetime, timedelta
from typing import Optional

from .database import SecurityDB
from ..config.settings import load_config

config = load_config()


class VaultManager:
    """Manage the encrypted secrets vault and rotation lifecycle."""

    def __init__(self, db: SecurityDB = None):
        self.db = db or SecurityDB()
        self.vault_path = config.vault_path
        self.vault_file = os.path.join(self.vault_path, "secrets.enc")
        self.vault_key_file = os.path.join(self.vault_path, "vault.key")
        self._aesgcm = None

    def _get_cipher(self):
        if self._aesgcm:
            return self._aesgcm
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        with open(self.vault_key_file) as f:
            key = bytes.fromhex(f.read().strip())
        self._aesgcm = AESGCM(key)
        return self._aesgcm

    def _load_vault(self) -> dict:
        if not os.path.exists(self.vault_file):
            return {}
        with open(self.vault_file) as f:
            return json.load(f)

    def _save_vault(self, data: dict):
        with open(self.vault_file, "w") as f:
            json.dump(data, f, indent=2)
        os.chmod(self.vault_file, 0o600)

    def _decrypt(self, entry: dict) -> str:
        cipher = self._get_cipher()
        nonce = bytes.fromhex(entry["nonce"])
        ct = base64.b64decode(entry["ciphertext"])
        return cipher.decrypt(nonce, ct, None).decode("utf-8")

    def _encrypt(self, plaintext: str) -> dict:
        cipher = self._get_cipher()
        nonce = os.urandom(12)
        ct = cipher.encrypt(nonce, plaintext.encode(), None)
        return {
            "ciphertext": base64.b64encode(ct).decode(),
            "nonce": nonce.hex(),
        }

    # ── Public API ───────────────────────────────────────

    def verify_integrity(self) -> dict:
        """Verify all vault entries can be decrypted."""
        vault = self._load_vault()
        results = {"ok": [], "failed": [], "total": len(vault)}

        for name, entry in vault.items():
            try:
                self._decrypt(entry)
                results["ok"].append(name)
            except Exception as e:
                results["failed"].append({"name": name, "error": str(e)})

        self.db.log_event(
            "vault_integrity_check",
            f"Vault check: {len(results['ok'])}/{results['total']} OK, {len(results['failed'])} failed",
            severity="critical" if results["failed"] else "info",
            source="vault-manager",
        )
        return results

    def get_secret(self, name: str) -> Optional[str]:
        """Decrypt and return a single secret."""
        vault = self._load_vault()
        entry = vault.get(name)
        if not entry:
            return None
        return self._decrypt(entry)

    def set_secret(self, name: str, value: str):
        """Encrypt and store a secret."""
        vault = self._load_vault()
        vault[name] = self._encrypt(value)
        self._save_vault(vault)
        self.db.log_event("secret_updated", f"Secret '{name}' updated in vault",
                          severity="info", source="vault-manager")

    def rotate_secret(self, name: str, new_value: str) -> dict:
        """Rotate a secret: store new value, update rotation tracking."""
        old_value = self.get_secret(name)
        self.set_secret(name, new_value)

        # Update rotation tracker
        self.db.track_secret(name, config.scan.secret_rotation_days)

        self.db.log_event(
            "secret_rotated",
            f"Secret '{name}' rotated",
            severity="info",
            source="vault-manager",
        )

        return {
            "name": name,
            "rotated": True,
            "had_previous": old_value is not None,
            "next_rotation_days": config.scan.secret_rotation_days,
        }

    def init_rotation_tracking(self):
        """Initialize rotation tracking for all vault secrets."""
        vault = self._load_vault()
        for name in vault:
            self.db.track_secret(name, config.scan.secret_rotation_days)
        return {"tracked": list(vault.keys())}

    def get_rotation_status(self) -> dict:
        """Get rotation status for all secrets."""
        all_secrets = self.db.get_rotation_status()
        overdue = self.db.get_overdue_rotations()
        return {
            "secrets": all_secrets,
            "overdue": overdue,
            "total": len(all_secrets),
            "overdue_count": len(overdue),
        }

    def list_secrets(self) -> list:
        """List secret names (never values)."""
        vault = self._load_vault()
        return list(vault.keys())

    def vault_status(self) -> dict:
        """Get vault health status."""
        exists = os.path.exists(self.vault_file)
        key_exists = os.path.exists(self.vault_key_file)
        secret_count = 0
        vault_mode = None
        key_mode = None

        if exists:
            secret_count = len(self._load_vault())
            vault_mode = oct(os.stat(self.vault_file).st_mode)[-3:]
        if key_exists:
            key_mode = oct(os.stat(self.vault_key_file).st_mode)[-3:]

        return {
            "initialized": exists and key_exists,
            "secret_count": secret_count,
            "vault_file": self.vault_file,
            "vault_permissions": vault_mode,
            "key_permissions": key_mode,
            "permissions_ok": vault_mode == "600" and key_mode == "600",
        }
