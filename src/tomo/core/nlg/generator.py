import logging
from typing import Optional, Text, Any

from tomo.core.bot_message import BotMessage
from tomo.shared.sessions import Session


logger = logging.getLogger(__name__)


class NaturalLanguageGenerator:
    """Generate bot utterances for TOMO based on a dialogue state."""

    async def generate(
        self,
        utter_action: Text,
        session: Session,
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[BotMessage]:
        return BotMessage(recipient_id="user", text=utter_action)
