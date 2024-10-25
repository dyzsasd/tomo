import time
import typing

from tomo.core.events import BotUttered
from tomo.shared.action import Action
from tomo.shared.event import Event
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session import Session


class ActionListen(Action):
    name = "listen"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pass


class ActionExtractSlots(Action):
    name = "extract_slots"

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pass


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
