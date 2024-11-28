import logging
from datetime import datetime
from typing import List

from ..core import TomoService
from ..models import SessionSummary

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
                created_at = (
                    datetime.fromtimestamp(events[0].timestamp) if events else None
                )
                last_active = (
                    datetime.fromtimestamp(events[-1].timestamp) if events else None
                )

                # Count messages
                message_count = len(session.get_conversation_messages())

                # Get current step if available
                current_step = session.slots.get("step")
                current_step_value = current_step.value if current_step else None

                summary = SessionSummary(
                    session_id=session_id,
                    created_at=created_at,
                    last_active=last_active,
                    message_count=message_count,
                    active=session.active,
                    current_step=current_step_value,
                )
                session_summaries.append(summary)

        return {"total_sessions": len(session_summaries), "sessions": session_summaries}

    except Exception as e:
        logger.error(f"Error getting session summaries: {e}", exc_info=True)
        raise e
