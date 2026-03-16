"""
Carbon6 Secrets Vault - Python reader.

AES-256-GCM encrypted secrets stored at /root/.carbon6-vault/secrets.enc
Key at /root/.carbon6-vault/vault.key

Usage:
    from lib.vault import get_secret, vault_status

    api_key = get_secret("PUSHCUT_API_KEY")
    jwt = get_secret("JWT_SECRET")
"""
import base64
import json
import os
from functools import lru_cache
from typing import Optional

VAULT_PATH = os.environ.get("VAULT_PATH", "/root/.carbon6-vault")
VAULT_FILE = os.path.join(VAULT_PATH, "secrets.enc")
VAULT_KEY_FILE = os.path.join(VAULT_PATH, "vault.key")

_cache: Optional[dict] = None


def _load_key() -> bytes:
    with open(VAULT_KEY_FILE) as f:
        return bytes.fromhex(f.read().strip())


def _decrypt(ciphertext_b64: str, nonce_hex: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    key = _load_key()
    aesgcm = AESGCM(key)
    nonce = bytes.fromhex(nonce_hex)
    ct = base64.b64decode(ciphertext_b64)
    plaintext = aesgcm.decrypt(nonce, ct, None)
    return plaintext.decode("utf-8")


def _load_vault() -> dict:
    global _cache
    if _cache is not None:
        return _cache

    _cache = {}
    if not os.path.exists(VAULT_FILE):
        return _cache

    with open(VAULT_FILE) as f:
        raw = json.load(f)

    for key, entry in raw.items():
        try:
            _cache[key] = _decrypt(entry["ciphertext"], entry["nonce"])
        except Exception as e:
            print(f"[Vault] Failed to decrypt {key}: {e}")

    return _cache


def get_secret(key: str, default: str = "") -> str:
    """Get a secret by key. Falls back to env var, then default."""
    vault = _load_vault()
    return vault.get(key) or os.environ.get(key) or default


def has_secret(key: str) -> bool:
    vault = _load_vault()
    return key in vault or key in os.environ


def list_keys() -> list:
    vault = _load_vault()
    return list(vault.keys())


def clear_cache():
    global _cache
    _cache = None


def vault_status() -> dict:
    return {
        "initialized": os.path.exists(VAULT_FILE),
        "key_exists": os.path.exists(VAULT_KEY_FILE),
        "secret_count": len(_load_vault()),
        "vault_path": VAULT_PATH,
    }
