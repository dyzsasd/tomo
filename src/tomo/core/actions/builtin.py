import typing

from tomo.core.policies.policy import PolicyPrediction

from tomo.shared.action import Action
from tomo.shared.event import Event
from tomo.shared.output_channel import OutputChannel
from tomo.shared.session import Session


class ActionListen(Action):
    name = "listen"
    async def run(self, output_channel: OutputChannel, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionExtractSlots(Action):
    name = "extract_slots"
    async def run(self, output_channel: OutputChannel, session: Session) -> typing.Optional[typing.List[Event]]:
        pass

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionSessionStart(Action):
    name = "session_start"
    greeting_message: typing.Text
    async def run(self, output_channel: OutputChannel, session: Session) -> typing.Optional[typing.List[Event]]:
        await output_channel.send_text_message(self.greeting_message)
        # TODO: return bot uttered event
        return []

    def event_for_successful_execution(self, policy: PolicyPrediction) -> typing.List[Event]:
        pass

class ActionDisableSession(Action):
    "Turn off action"
