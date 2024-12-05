from enum import Enum


class SessionStatus(str, Enum):
    """Enum for session status"""

    ACTIVE = "active"
    PENDING = "pending"
    ARCHIVED = "archived"
    DELETED = "deleted"
