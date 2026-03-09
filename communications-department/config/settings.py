"""Communications Department Configuration.

All secrets loaded from environment variables.
Set these in /root/carbon6-platform/.env or export them.
"""
import os
from dataclasses import dataclass, field


@dataclass
class TwilioConfig:
    account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))
    phone_number: str = field(default_factory=lambda: os.getenv("TWILIO_PHONE_NUMBER", ""))
    webhook_url: str = field(default_factory=lambda: os.getenv("TWILIO_WEBHOOK_URL", ""))

    @property
    def is_configured(self) -> bool:
        return bool(self.account_sid and self.auth_token and self.phone_number)


@dataclass
class EmailConfig:
    # SMTP (for sending)
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))

    # IMAP (for receiving)
    imap_host: str = field(default_factory=lambda: os.getenv("IMAP_HOST", "imap.gmail.com"))
    imap_port: int = field(default_factory=lambda: int(os.getenv("IMAP_PORT", "993")))
    imap_user: str = field(default_factory=lambda: os.getenv("IMAP_USER", ""))
    imap_password: str = field(default_factory=lambda: os.getenv("IMAP_PASSWORD", ""))

    # SendGrid (optional, for bulk/tracking)
    sendgrid_api_key: str = field(default_factory=lambda: os.getenv("SENDGRID_API_KEY", ""))

    # Additional accounts (JSON list in env)
    additional_accounts: str = field(default_factory=lambda: os.getenv("EMAIL_ADDITIONAL_ACCOUNTS", "[]"))

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_user and self.smtp_password)

    @property
    def imap_configured(self) -> bool:
        return bool(self.imap_user and self.imap_password)

    @property
    def sendgrid_configured(self) -> bool:
        return bool(self.sendgrid_api_key)


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_COMMS_DB", "2")))
    prefix: str = "comms:"


@dataclass
class DatabaseConfig:
    url: str = field(default_factory=lambda: os.getenv(
        "COMMS_DATABASE_URL",
        "postgresql://root@localhost/carbon6"
    ))
    schema: str = "communications"


@dataclass
class CommsConfig:
    twilio: TwilioConfig = field(default_factory=TwilioConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 3100
    api_prefix: str = "/api/comms"

    # Worker settings
    worker_concurrency: int = 4
    retry_max: int = 3
    retry_delay: int = 60  # seconds


def load_config() -> CommsConfig:
    """Load configuration from environment."""
    return CommsConfig()
