# TODO: implement nlu parser
import logging

from tomo.core.user_message import UserMessage
from tomo.shared.session import Session


logger = logging.getLogger(__name__)


class NLUParser:
    async def parse(self, message: UserMessage, session: Session) -> dict:
        logger.debug(f"processing {message.text}")
        logger.debug(f"processing session: {session}")
        return {
            "intent": [],
            "entities": [],
        }
