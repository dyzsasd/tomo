import json
import logging
import os
import time
from copy import deepcopy
from pathlib import Path
from typing import Optional, Dict, List
import glob

from aiofiles import open as aio_open
from aiofiles.os import remove as aio_remove

from tomo.assistant import Assistant
from tomo.core.events import BotUttered, UserUttered
from tomo.shared.event import Event
from tomo.shared.exceptions import TomoFatalException, TomoException
from tomo.shared.session import Session
from tomo.shared.session_manager import SessionManager
from tomo.shared.slots import Slot


logger = logging.getLogger(__name__)


class FileSession(Session):
    """Session implementation that works with FileSessionManager"""

    def __init__(
        self,
        session_manager: "FileSessionManager",
        session_id: str,
        max_event_history: Optional[int] = None,
        slots: Optional[Dict[str, Slot]] = None,
    ) -> None:
        """
        Initialize a file-based session

        Args:
            session_manager: The FileSessionManager instance
            session_id: Unique identifier for the session
            max_event_history: Maximum number of events to store
            slots: Dictionary of slots for the session
        """
        super().__init__(
            session_id=session_id, max_event_history=max_event_history, slots=slots
        )
        self.session_manager: "FileSessionManager" = session_manager

    async def update_with_event(
        self, event: Event, immediate_persist: bool = True
    ) -> None:
        """
        Add a new event to the session's event history and update the session state

        Args:
            event: The event to add
            immediate_persist: Whether to save to file immediately
        """
        if getattr(self, "session_manager") is None:
            raise TomoFatalException(
                "session_manager isn't defined in this instance, event cannot be applied."
            )

        event.apply_to(self)
        self.events.append(event)
        logger.debug(
            f"Event {event.__class__.__name__} has been applied to session {self.session_id}"
        )

        if immediate_persist:
            persisted_session = await self.session_manager.save(self)
            return persisted_session
        return self

    async def update_with_events(
        self,
        new_events: List[Event],
        override_timestamp: bool = True,
    ) -> Session:
        """
        Update session with multiple events

        Args:
            new_events: List of events to apply
            override_timestamp: Whether to update event timestamps
        """
        if getattr(self, "session_manager") is None:
            raise TomoFatalException(
                "session_manager isn't defined in this instance, event cannot be applied."
            )

        for e in new_events:
            if override_timestamp:
                e.timestamp = time.time()
            await self.update_with_event(e, immediate_persist=False)

        # Save all changes at once
        persisted_session = await self.session_manager.save(self)
        return persisted_session

    def last_user_uttered_event(self) -> Optional[Event]:
        """Get the most recent UserUttered event"""
        for event in reversed(self.events):
            if isinstance(event, UserUttered):
                return event
        return None

    def has_bot_replied(self) -> bool:
        """Check if the bot has replied since the last user message"""
        for event in reversed(self.events):
            if isinstance(event, BotUttered):
                return True
            if isinstance(event, UserUttered):
                return False
        return False

    def get_events_after(self, timestamp: float) -> List[Event]:
        """
        Get all events after a specific timestamp

        Args:
            timestamp: The timestamp to filter events

        Returns:
            List of events after the timestamp
        """
        return [event for event in self.events if event.timestamp > timestamp]

    def get_conversation_messages(self) -> List[Dict]:
        """
        Get conversation messages in a format suitable for chat interfaces

        Returns:
            List of message dictionaries
        """
        messages = []
        for event in self.events:
            if isinstance(event, (UserUttered, BotUttered)):
                message = {
                    "text": event.text,
                    "timestamp": event.timestamp,
                    "type": "user" if isinstance(event, UserUttered) else "bot",
                }
                if hasattr(event, "metadata") and event.metadata:
                    message["metadata"] = event.metadata
                messages.append(message)
        return message


class FileSessionManager(SessionManager):
    """Session manager that stores each session in a separate JSON file"""

    def __init__(
        self,
        assistant: Assistant,
        storage_path: str = "sessions",
        file_extension: str = ".json",
    ):
        """
        Initialize the file session manager

        Args:
            assistant: The assistant instance containing slot definitions
            storage_path: Directory path where session files will be stored
            file_extension: File extension for session files
        """
        self.assistant = assistant
        self.storage_path = Path(storage_path)
        self.file_extension = file_extension
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Ensure the storage directory exists"""
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, session_id: str) -> Path:
        """Get the full path for a session file"""
        safe_session_id = "".join(
            c for c in session_id if c.isalnum() or c in ("-", "_")
        )
        return self.storage_path / f"{safe_session_id}{self.file_extension}"

    async def _read_session_file(self, file_path: Path) -> Optional[dict]:
        """Read and parse a session file"""
        try:
            async with aio_open(file_path, "r") as file:
                content = await file.read()
                return json.loads(content)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding session file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading session file {file_path}: {e}")
            return None

    async def _write_session_file(self, file_path: Path, session_data: dict):
        """Write session data to file"""
        try:
            async with aio_open(file_path, "w") as file:
                await file.write(json.dumps(session_data, indent=2))
        except Exception as e:
            logger.error(f"Error writing session file {file_path}: {e}")
            raise TomoException(f"Failed to save session: {e}") from e

    async def get_or_create_session(
        self, session_id: str, max_event_history: Optional[int] = None
    ) -> Session:
        """
        Get an existing session or create a new one

        Args:
            session_id: The session identifier
            max_event_history: Maximum number of events to store

        Returns:
            The session instance
        """
        session = await self.get_session(session_id)
        if session is None:
            # Initialize new session with assistant slots
            slots = {slot.name: deepcopy(slot) for slot in self.assistant.slots}
            session = FileSession(
                session_manager=self,
                session_id=session_id,
                max_event_history=max_event_history,
                slots=slots,
            )
            await self.save(session)
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID

        Args:
            session_id: The session identifier

        Returns:
            The session instance if found, None otherwise
        """
        file_path = self._get_session_path(session_id)
        session_data = await self._read_session_file(file_path)

        if session_data is None:
            return None

        try:
            return Session.from_dict(session_data)
        except Exception as e:
            logger.error(f"Error deserializing session {session_id}: {e}")
            return None

    async def save(self, session: Session) -> Session:
        """
        Save a session to file

        Args:
            session: The session to save

        Returns:
            The saved session instance
        """
        file_path = self._get_session_path(session.session_id)

        # Add metadata for session management
        session_data = session.to_dict()
        session_data["_metadata"] = {"last_modified": time.time()}

        await self._write_session_file(file_path, session_data)
        return session

    async def delete_session(self, session_id: str) -> None:
        """
        Delete a session

        Args:
            session_id: The session identifier to delete
        """
        file_path = self._get_session_path(session_id)
        try:
            await aio_remove(file_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.error(f"Error deleting session file {file_path}: {e}")
            raise TomoException(f"Failed to delete session: {e}") from e

    async def cleanup_old_sessions(self, max_age_days: int = 30) -> None:
        """
        Delete sessions older than specified days

        Args:
            max_age_days: Maximum age of sessions in days
        """
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)

        # Get all session files
        pattern = str(self.storage_path / f"*{self.file_extension}")
        session_files = glob.glob(pattern)

        for file_path in session_files:
            try:
                session_data = await self._read_session_file(Path(file_path))
                if (
                    session_data
                    and session_data.get("_metadata", {}).get("last_modified", 0)
                    < cutoff_time
                ):
                    await aio_remove(file_path)
                    logger.info(f"Deleted old session file: {file_path}")
            except Exception as e:
                logger.error(f"Error cleaning up session file {file_path}: {e}")

    async def list_sessions(self) -> list[str]:
        """
        List all active session IDs

        Returns:
            List of session IDs
        """
        pattern = str(self.storage_path / f"*{self.file_extension}")
        session_files = glob.glob(pattern)
        return [Path(f).stem for f in session_files]

    async def get_session_stats(self) -> dict:
        """
        Get statistics about stored sessions

        Returns:
            Dictionary containing session statistics
        """
        total_sessions = 0
        active_sessions = 0
        total_size = 0

        pattern = str(self.storage_path / f"*{self.file_extension}")
        session_files = glob.glob(pattern)

        for file_path in session_files:
            total_sessions += 1
            total_size += os.path.getsize(file_path)

            try:
                session_data = await self._read_session_file(Path(file_path))
                if session_data and session_data.get("active", False):
                    active_sessions += 1
            except Exception:
                continue

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_size_bytes": total_size,
            "storage_path": str(self.storage_path),
        }
