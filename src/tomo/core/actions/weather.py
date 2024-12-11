import logging
import typing

from tomo.core.events import SlotSet
from tomo.shared.action import Action
from tomo.core.events.base import Event
from tomo.shared.output_channel import OutputChannel
from tomo.core.session import Session


logger = logging.getLogger(__name__)


class FindWeather(Action):
    name: typing.ClassVar[str] = "find_weather"
    description: typing.ClassVar[
        str
    ] = "Find the weather information according to the location and date"

    @classmethod
    def required_slots(cls):
        return [
            "date",
            "city",
        ]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        date = session.slots.get("date")
        city = session.slots.get("city")
        logger.debug(f"Getting the weather information for {city} at {date}")
        return [
            SlotSet(
                key="weather",
                value="There will be heavy snow, and the temperature will be between -5 degree.",
            )
        ]
