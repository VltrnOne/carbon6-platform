"""Communications Department Engine - Core messaging infrastructure."""
from .database import CommsDB
from .sms import SMSEngine
from .email_engine import EmailEngine
from .voice import VoiceEngine
from .contacts import ContactManager
from .search import SearchEngine
from .router import MessageRouter
from .scheduler import MessageScheduler
from .inbox import UnifiedInbox
from .analytics import AnalyticsEngine

__all__ = [
    "CommsDB",
    "SMSEngine",
    "EmailEngine",
    "VoiceEngine",
    "ContactManager",
    "SearchEngine",
    "MessageRouter",
    "MessageScheduler",
    "UnifiedInbox",
    "AnalyticsEngine",
]
