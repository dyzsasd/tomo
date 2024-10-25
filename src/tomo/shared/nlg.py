import abc
import logging
from typing import Any, Optional

from tomo.shared.bot_message import BotMessage
from tomo.shared.session import Session

logger = logging.getLogger(__name__)


class NaturalLanguageGenerator(abc.ABC):
    """Generate bot utterances for TOMO based on a dialogue state."""

    @abc.abstractmethod
    async def generate(
        self,
        utter_action: str,
        session: Session,
        output_channel: str,
        **kwargs: Any,
    ) -> Optional[BotMessage]:
        pass
