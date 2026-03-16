"""Security Department Configuration.

All secrets loaded from vault, fallback to environment variables.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

# Load .env
_env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file, override=False)
    except ImportError:
        with open(_env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    key, val = key.strip(), val.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = val


def _load_redis_password() -> str:
    try:
        with open("/root/.redis_password", "r") as f:
            return f.read().strip()
    except Exception:
        return os.getenv("REDIS_PASSWORD", "")


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = 4
    password: str = field(default_factory=_load_redis_password)
    prefix: str = "security:"


@dataclass
class DatabaseConfig:
    url: str = field(default_factory=lambda: os.getenv(
        "SECURITY_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql://root@localhost/carbon6")
    ))
    schema: str = "security"


@dataclass
class AlertConfig:
    """Thresholds and notification settings."""
    cvss_alert_threshold: float = 7.0
    brute_force_threshold: int = 50      # failed attempts in window
    brute_force_window: int = 3600       # 1 hour
    cert_expiry_warn_days: int = 14
    disk_usage_warn_pct: int = 85
    disk_usage_crit_pct: int = 95
    notify_hermes: bool = True           # Send alerts via HERMES
    notify_channel: str = "imessage"     # Default alert channel


@dataclass
class ScanConfig:
    """Scanner intervals (seconds)."""
    threat_scan_interval: int = 300      # 5 min
    vuln_scan_interval: int = 3600       # 1 hour
    compliance_interval: int = 86400     # daily
    log_analysis_interval: int = 600     # 10 min
    secret_rotation_days: int = 90       # rotate secrets every N days


@dataclass
class SentinelConfig:
    redis: RedisConfig = field(default_factory=RedisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    alert: AlertConfig = field(default_factory=AlertConfig)
    scan: ScanConfig = field(default_factory=ScanConfig)

    # API settings
    api_host: str = "127.0.0.1"
    api_port: int = 3300

    # Paths
    vault_path: str = "/root/.carbon6-vault"
    log_dir: str = "/root/security/logs"
    auth_log: str = "/var/log/auth.log"
    nginx_log_dir: str = "/var/log/nginx"

    # Worker settings
    worker_concurrency: int = 2


def load_config() -> SentinelConfig:
    return SentinelConfig()
