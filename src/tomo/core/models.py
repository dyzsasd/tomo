from enum import Enum


class SessionStatus(str, Enum):
    """Enum for session status"""

    ACTIVE = "active"
    PENDING = "pending"
    WAITING = "waiting"
    ARCHIVED = "archived"
    DELETED = "deleted"
