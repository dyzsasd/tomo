import logging

from ..core import TomoService

logger = logging.getLogger(__name__)


async def get_slots(session_id: str, tomo_service: TomoService):
    """Get all slots for a session"""
    try:
        slots = await tomo_service.get_session_slots(session_id)
        return {"session_id": session_id, "slots": slots}
    except Exception as e:
        logger.error(f"Error getting session slots: {e}", exc_info=True)
        raise e
