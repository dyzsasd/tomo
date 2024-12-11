from copy import deepcopy
from datetime import datetime, timezone
import glob
import json
import logging
import os
import time
from typing import Optional
from pathlib import Path

from aiofiles import open as aio_open
from aiofiles.os import remove as aio_remove

from tomo.assistant import Assistant
from tomo.core.events import Event
from tomo.core.models import SessionStatus
from tomo.core.session import Session
from tomo.shared.exceptions import TomoException
from tomo.shared.slots import Slot
from tomo.utils.json import JsonEngine

from .base import SessionManager


logger = logging.getLogger(__name__)


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

    async def create_session(self, session_id: Optional[str] = None) -> "Session":
        """
        Get an existing session or create a new one

        Args:
            session_id: The session identifier
        Returns:
            The session instance
        """
        if session_id is None:
            session_id = str(int(time.time()))

        session_ids = await self.list_sessions()
        if session_id in session_ids:
            raise RuntimeError(
                f"Cannot create session, session id {session_id} exist already !"
            )

        logger.info(f"creating new session {session_id}")
        # Initialize new session with assistant slots
        slots = {slot.name: deepcopy(slot) for slot in self.assistant.slots}
        session = Session(
            session_id=session_id,
            slots=slots,
            status=SessionStatus.ACTIVE,
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
            return self.from_dict(session_data)
        except Exception as e:
            logger.error(f"Error deserializing session {session_id}: {e}")
            raise e

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
        session_data = self.to_dict(session)
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

    def to_dict(self, session: Session):
        return {
            "session_id": session.session_id,
            "events": [JsonEngine.to_json(event) for event in session.events],
            "slots": {
                key: JsonEngine.to_json(slot) for key, slot in session.slots.items()
            },
            "status": session.status,
            "metadata": session.metadata,
            "created_at": session.created_at.isoformat(),
        }

    def from_dict(self, data: dict):
        session_id = data["session_id"]
        events = [
            JsonEngine.from_json(event_data, Event) for event_data in data["events"]
        ]
        slots = {
            key: JsonEngine.from_json(slot_data, Slot)
            for key, slot_data in data["slots"].items()
        }
        status = data.get("status")
        metadata = data.get("metadata", {})
        created_at_str = data.get("created_at")
        if created_at_str is None:
            created_at = datetime.now(timezone.utc)
        else:
            created_at = datetime.fromisoformat(created_at_str)
        session = Session(
            session_id=session_id,
            slots=slots,
            created_at=created_at,
            status=status,
            events=events,
            metadata=metadata,
        )

        return session
