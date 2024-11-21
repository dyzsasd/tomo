import logging

from ..core import TomoService

logger = logging.getLogger(__name__)


async def get_conversations(session_id: str, tomo_service: TomoService):
    """Get conversation messages for a session"""
    try:
        messages = await tomo_service.get_conversation_messages(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}", exc_info=True)
        raise e
