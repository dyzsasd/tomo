# TODO: implement nlu parser

from tomo.core.user_message import UserMessage
from tomo.shared.sessions import Session


class NLUParser:
    async def parse(self, message: UserMessage, session: Session) -> dict:
        return {
            "intent": [],
            "entities": [],
        }
