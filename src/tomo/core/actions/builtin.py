import logging
import time
import typing

from tomo.core.events import BotUttered, UserUttered, SlotSet
from tomo.nlu.models import Entity
from tomo.shared.action import Action
from tomo.shared.event import Event
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session import Session


logger = logging.getLogger(__name__)


class ActionListen(Action):
    name = "listen"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pass


class ActionBotUtter(Action):
    name = "bot_utter"
    message: str

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        await output_channel.send_text_message(self.message)
        return [
            BotUttered(
                text=self.message,
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class ActionBotUtterQuickReply(ActionBotUtter):
    name = "bot_utter_quick_reply"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        if not session.has_bot_replied():
            await output_channel.send_text_message(self.message)
            logger.debug(f"Quick {self.message} reply has been sent.")
            return [
                BotUttered(
                    text=self.message,
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]
        return []


class ActionExtractSlots(Action):
    name = "extract_slots"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        user_uttered: UserUttered = session.last_user_uttered_event()

        if user_uttered is None or not isinstance(user_uttered, UserUttered):
            return []

        events = []
        new_entities: typing.List[Entity] = (
            user_uttered and user_uttered.entities
        ) or []
        for entity in new_entities:
            if entity.name not in session.slots:
                logger.warning(
                    f"Extracted entity {entity.name} are not in session's defined slots"
                )
                continue
            logger.debug(f"Generating SlotSet event of {entity.name}")
            events.append(
                SlotSet(
                    key=entity.name,
                    value=entity.value,
                    timestamp=time.time(),
                    metadata=None,
                )
            )
        return events


class ActionSessionStart(Action):
    name = "session_start"
    greeting_message: str

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        await output_channel.send_text_message(self.greeting_message)
        return [
            BotUttered(
                text=self.greeting_message,
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class ActionDisableSession(Action):
    "Turn off action"
