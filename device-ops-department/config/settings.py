"""Device Operations Department Configuration."""
import os
from dataclasses import dataclass, field


@dataclass
class PushcutConfig:
    api_key: str = field(default_factory=lambda: os.getenv("PUSHCUT_API_KEY", ""))
    device_name: str = field(default_factory=lambda: os.getenv("PUSHCUT_DEVICE_NAME", ""))
    base_url: str = "https://api.pushcut.io"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.device_name)


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DEVOPS_DB", "3")))
    prefix: str = "devops:"


@dataclass
class DatabaseConfig:
    url: str = field(default_factory=lambda: os.getenv(
        "DEVICEOPS_DATABASE_URL",
        os.getenv("DATABASE_URL", "postgresql://root@localhost/carbon6")
    ))


@dataclass
class MonitorConfig:
    poll_interval: int = 300  # seconds
    battery_alert_threshold: int = 20
    storage_alert_threshold_gb: int = 5


@dataclass
class DeviceOpsConfig:
    pushcut: PushcutConfig = field(default_factory=PushcutConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)

    api_host: str = "0.0.0.0"
    api_port: int = 3200
    webhook_base: str = field(default_factory=lambda: os.getenv("AEGIS_WEBHOOK_URL", "https://aegis.vltrn.cloud"))


def load_config() -> DeviceOpsConfig:
    return DeviceOpsConfig()
