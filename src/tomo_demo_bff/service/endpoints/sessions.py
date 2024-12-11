import logging
from typing import List, Optional

from fastapi import HTTPException

from tomo.core.models import SessionStatus
from tomo.core.session import Session

from ..core import TomoService
from ..models import (
    CreatePNRSessionRequest,
    CreatePNRSessionResponse,
    SessionSummary,
    PNRSession,
    PNRSessionsResponse,
    SessionType,
)

logger = logging.getLogger(__name__)


async def get_all_sessions(tomo_service: TomoService) -> dict:
    """Get all sessions with their summaries"""
    try:
        # Get all session IDs
        session_ids = await tomo_service.session_manager.list_sessions()

        # Collect summaries for each session
        session_summaries: List[SessionSummary] = []
        for session_id in session_ids:
            session = await tomo_service.session_manager.get_session(session_id)
            if session:
                # Get first and last event timestamps
                events = session.events
                created_at = session.created_at
                last_active = events[-1].timestamp if events else session.created_at

                # Count messages
                message_count = len(session.get_conversation_messages())

                summary = SessionSummary(
                    session_id=session_id,
                    created_at=created_at,
                    last_active=last_active,
                    message_count=message_count,
                    status=session.status,
                )
                session_summaries.append(summary)

        return {"total_sessions": len(session_summaries), "sessions": session_summaries}

    except Exception as e:
        logger.error(f"Error getting session summaries: {e}", exc_info=True)
        raise e


async def delete_session(session_id: str, tomo_service: TomoService) -> None:
    return await tomo_service.session_manager.delete_session(session_id)


async def get_pnr_sessions(tomo_service: TomoService) -> PNRSessionsResponse:
    """Get all PNR check sessions"""
    try:
        session_ids = await tomo_service.session_manager.list_sessions()

        pnr_sessions: List[PNRSession] = []
        for session_id in session_ids:
            session = await tomo_service.session_manager.get_session(session_id)
            if (
                session
                and session.metadata.get("session_type") == SessionType.PNR_ASSISTANT
            ):
                pnr_number = session.slots.get("pnr_number")
                status = session.slots.get("status", SessionStatus.ACTIVE)

                # Get event timestamps
                events = session.events
                created_at = events[0].timestamp if events else None
                last_active = events[-1].timestamp if events else None

                # Only include non-deleted sessions
                if status != SessionStatus.DELETED:
                    pnr_session = PNRSession(
                        session_id=session_id,
                        pnr_number=pnr_number.value,
                        created_at=created_at,
                        last_active=last_active,
                        status=status.value,
                        session_type=SessionType.PNR_ASSISTANT,
                        message_count=len(session.get_conversation_messages()),
                    )
                    pnr_sessions.append(pnr_session)

        return PNRSessionsResponse(
            total_sessions=len(pnr_sessions), sessions=pnr_sessions
        )
    except Exception as e:
        logger.error(f"Error getting PNR sessions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def create_pnr_session(
    request: CreatePNRSessionRequest, tomo_service: TomoService
) -> CreatePNRSessionResponse:
    """Create or retrieve a session for PNR check"""
    try:
        # Check if session already exists for this PNR
        existing_session = await find_pnr_session(request.pnr_number, tomo_service)
        if existing_session:
            return CreatePNRSessionResponse(
                session_id=existing_session.session_id, session=existing_session
            )

        # Create new session
        session = await tomo_service.session_manager.create_session()

        # Set session metadata
        session.metadata["session_type"] = SessionType.PNR_ASSISTANT

        # Initialize session slots
        session.metadata["pnr_number"] = request.pnr_number
        session.status = SessionStatus.ACTIVE

        await tomo_service.session_manager.save(session)

        return CreatePNRSessionResponse(
            session_id=session.session_id, session=_pnr_session_from_session(session)
        )
    except Exception as e:
        logger.error(f"Error creating PNR session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


async def find_pnr_session(
    pnr_number: str, tomo_service: TomoService
) -> Optional[PNRSession]:
    """Helper function to find an existing active session for a PNR"""
    session_ids = await tomo_service.session_manager.list_sessions()

    for session_id in session_ids:
        session = await tomo_service.session_manager.get_session(session_id)
        if (
            session
            and session.metadata.get("session_type") == SessionType.PNR_ASSISTANT
        ):
            session_pnr_number = session.metadata.get("pnr_number")
            status = session.status
            if session_pnr_number == pnr_number and status == SessionStatus.ACTIVE:
                return _pnr_session_from_session(session)

    return None


def _pnr_session_from_session(session: Session) -> PNRSession:
    events = session.events
    session_pnr_number = session.metadata.get("pnr_number")
    return PNRSession(
        session_id=session.session_id,
        pnr_number=session_pnr_number,
        created_at=session.created_at,
        last_active=events[-1].timestamp if events else session.created_at,
        status=SessionStatus.ACTIVE,
        session_type=SessionType.PNR_ASSISTANT,
        message_count=len(session.get_conversation_messages()),
    )
