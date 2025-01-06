import logging
from typing import List

from fastapi import HTTPException

from ..core import TomoService
from ..models import SessionSummary, PendingAction, PendingActionsResponse

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


async def get_pending_actions(session_id: str, tomo_service: TomoService):
    """Get all sessions with their summaries"""
    try:
        session = await tomo_service.session_manager.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=400, detail=f"Session {session_id} not found."
            )
        pending_actions = [
            PendingAction(session_id=session_id, action_name=action.name)
            for action in session.pending_actions
        ]
        return PendingActionsResponse(pending_actions=pending_actions)

    except Exception as e:
        if not isinstance(e, HTTPException):
            logger.error(f"Error getting session summaries: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e)) from e
        raise e
