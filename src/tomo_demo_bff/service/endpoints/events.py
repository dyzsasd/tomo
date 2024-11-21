import logging
from typing import Optional

from ..core import TomoService

logger = logging.getLogger(__name__)


async def get_session_events(
    session_id: str, after: Optional[float], tomo_service: TomoService
):
    """Get events for a session with optional timestamp filter"""
    try:
        events = await tomo_service.get_session_events(session_id, after)
        return {"session_id": session_id, "events": events}
    except Exception as e:
        logger.error(f"Error getting session events: {e}", exc_info=True)
        raise e
