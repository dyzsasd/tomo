# pylint: disable=C0301
# Line too long

import logging
import time
import typing

from tomo.core.events import (
    SlotSet,
    BotUttered,
    SessionDisabled,
)
from tomo.shared.action import Action
from tomo.core.events.base import Event
from tomo.shared.output_channel import OutputChannel
from tomo.core.session import Session
from tomo.shared.exceptions import TomoFatalException

logger = logging.getLogger(__name__)


class ValidateServiceAvailability(Action):
    name: typing.ClassVar[str] = "validate_service_availability"
    description: typing.ClassVar[
        str
    ] = "Validate if the service is available in the client's market."

    @classmethod
    def required_slots(cls):
        return ["client_location"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        client_location = session.slots.get("client_location")
        if not client_location:
            logger.debug("Client location not provided.")
            await output_channel.send_text_message(
                "Could you please provide your location?"
            )
            return [
                BotUttered(
                    text="Could you please provide your location?",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual service availability check
        service_available = True  # Assume service is available

        if service_available:
            logger.debug(f"Service is available in {client_location}.")
            return []

        logger.debug(f"Service is not available in {client_location}.")
        await output_channel.send_text_message(
            "Sorry, our service is not available in your location."
        )
        return [
            BotUttered(
                text="Sorry, our service is not available in your location.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            ),
            SessionDisabled(),
        ]


class ActionExchangeShopping(Action):
    name: typing.ClassVar[str] = "exchange_shopping"
    description: typing.ClassVar[
        str
    ] = "Validate if the service is available in the client's market."

    @classmethod
    def required_slots(cls):
        return ["pnr_details", "new_itinerary"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        client_location = session.slots.get("client_location")
        if not client_location:
            logger.debug("Client location not provided.")
            await output_channel.send_text_message(
                "Could you please provide your location?"
            )
            return [
                BotUttered(
                    text="Could you please provide your location?",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual service availability check
        service_available = True  # Assume service is available

        if service_available:
            logger.debug(f"Service is available in {client_location}.")
            return []

        logger.debug(f"Service is not available in {client_location}.")
        await output_channel.send_text_message(
            "Sorry, our service is not available in your location."
        )
        return [
            BotUttered(
                text="Sorry, our service is not available in your location.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            ),
            SessionDisabled(),
        ]


class RetrievePNR(Action):
    name: typing.ClassVar[str] = "retrieve_pnr"
    description: typing.ClassVar[
        str
    ] = "Retrieve the Passenger Name Record (PNR) details using TravelItineraryReadLLSRQ."

    @classmethod
    def required_slots(cls):
        return ["pnr_number"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        slot = session.slots.get("pnr_number")
        if not slot:
            raise TomoFatalException("pnr_number is missing")

        pnr_number = slot.value
        # Placeholder for actual PNR retrieval
        logger.debug(f"Retrieving PNR details for {pnr_number}.")
        pnr_details = {"pnr_number": pnr_number}  # Mocked PNR details

        if not pnr_details:
            raise TomoFatalException(f"Cannot retrieve the PNR for {pnr_number}")

        logger.debug(f"PNR details retrieved for {pnr_number}.")
        return [
            SlotSet(
                key="pnr_details",
                value=pnr_details,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class CancelExistingItinerary(Action):
    name: typing.ClassVar[str] = "cancel_existing_itinerary"
    description: typing.ClassVar[
        str
    ] = "Cancel the existing itinerary in the PNR using OTA_CancelLLSRQ."

    @classmethod
    def required_slots(cls):
        return ["pnr_details"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pnr_details = session.slots.get("pnr_details")
        if not pnr_details:
            logger.debug("PNR details not available.")
            await output_channel.send_text_message(
                "Cannot cancel itinerary without PNR details."
            )
            return [
                BotUttered(
                    text="Cannot cancel itinerary without PNR details.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual cancellation
        logger.debug(f"Cancelling itinerary for PNR {pnr_details['pnr_number']}.")
        cancellation_success = True  # Assume success

        if cancellation_success:
            logger.debug("Itinerary cancelled successfully.")
            return []

        logger.debug("Failed to cancel itinerary.")
        await output_channel.send_text_message(
            "Failed to cancel your existing itinerary."
        )
        return [
            BotUttered(
                text="Failed to cancel your existing itinerary.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class BookNewItinerary(Action):
    name: typing.ClassVar[str] = "book_new_itinerary"
    description: typing.ClassVar[
        str
    ] = "Book the new air itinerary as requested by the client using OTA_AirBookLLSRQ or EnhancedAirBookRQ."

    @classmethod
    def required_slots(cls):
        return ["new_itinerary_details"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        new_itinerary_details = session.slots.get("new_itinerary_details")
        if not new_itinerary_details:
            logger.debug("New itinerary details not provided.")
            await output_channel.send_text_message(
                "Please provide the details of your new itinerary."
            )
            return [
                BotUttered(
                    text="Please provide the details of your new itinerary.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual booking
        logger.debug(f"Booking new itinerary: {new_itinerary_details}")
        booking_success = True  # Assume success

        if booking_success:
            logger.debug("New itinerary booked successfully.")
            return []

        logger.debug("Failed to book new itinerary.")
        await output_channel.send_text_message("Unable to book your new itinerary.")
        return [
            BotUttered(
                text="Unable to book your new itinerary.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class PriceTheExchange(Action):
    name: typing.ClassVar[str] = "price_the_exchange"
    description: typing.ClassVar[
        str
    ] = "Price the exchange based on the new itinerary and calculate any additional fees or refunds using AutomatedExchangesLLSRQ."

    @classmethod
    def required_slots(cls):
        return ["original_ticket_number", "new_itinerary_details"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        original_ticket_number = session.slots.get("original_ticket_number")
        new_itinerary_details = session.slots.get("new_itinerary_details")
        if not original_ticket_number or not new_itinerary_details:
            logger.debug("Missing information for pricing the exchange.")
            await output_channel.send_text_message(
                "I need your original ticket number to price the exchange."
            )
            return [
                BotUttered(
                    text="I need your original ticket number to price the exchange.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual pricing
        logger.debug(f"Pricing exchange for ticket {original_ticket_number}")
        pricing_information = {
            "additional_fee": 150.00,
            "refund": 0.00,
            "pqr_number": "PQR123456",
        }

        if pricing_information:
            logger.debug("Pricing information obtained.")
            return [
                SlotSet(
                    key="pricing_information",
                    value=pricing_information,
                    timestamp=time.time(),
                    metadata=None,
                ),
                SlotSet(
                    key="pqr_number",
                    value=pricing_information["pqr_number"],
                    timestamp=time.time(),
                    metadata=None,
                ),
            ]

        logger.debug("Failed to obtain pricing information.")
        await output_channel.send_text_message(
            "Unable to obtain pricing information at this time."
        )
        return [
            BotUttered(
                text="Unable to obtain pricing information at this time.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class EvaluatePricingInformation(Action):
    name: typing.ClassVar[str] = "evaluate_pricing_information"
    description: typing.ClassVar[
        str
    ] = "Evaluate the returned pricing information and decide whether to proceed or ignore the transaction."

    @classmethod
    def required_slots(cls):
        return ["pricing_information"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pricing_information = session.slots.get("pricing_information")
        if not pricing_information:
            logger.debug("No pricing information to evaluate.")
            await output_channel.send_text_message(
                "There is no pricing information to evaluate."
            )
            return [
                BotUttered(
                    text="There is no pricing information to evaluate.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Present pricing to the user
        additional_fee = pricing_information.get("additional_fee")
        message = (
            f"The exchange will cost an additional ${additional_fee:.2f}. "
            "Would you like to proceed?"
        )
        await output_channel.send_text_message(message)
        return [
            BotUttered(
                text=message,
                data=None,
                timestamp=time.time(),
                metadata=None,
            ),
            # Wait for user confirmation
            SlotSet(
                key="awaiting_user_confirmation",
                value=True,
                timestamp=time.time(),
                metadata=None,
            ),
        ]


class ConfirmExchange(Action):
    name: typing.ClassVar[str] = "confirm_exchange"
    description: typing.ClassVar[
        str
    ] = "Confirm and store the exchange using ExchangeConfirmation in AutomatedExchangesLLSRQ."

    @classmethod
    def required_slots(cls):
        return ["pqr_number"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pqr_number = session.slots.get("pqr_number")
        if not pqr_number:
            logger.debug("PQR number not available.")
            await output_channel.send_text_message(
                "Cannot confirm exchange without a PQR number."
            )
            return [
                BotUttered(
                    text="Cannot confirm exchange without a PQR number.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual confirmation
        logger.debug(f"Confirming exchange with PQR number {pqr_number}.")
        confirmation_success = True  # Assume success

        if confirmation_success:
            logger.debug("Exchange confirmed successfully.")
            return []

        logger.debug("Failed to confirm exchange.")
        await output_channel.send_text_message("Failed to confirm your exchange.")
        return [
            BotUttered(
                text="Failed to confirm your exchange.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class EndAndRetrieveUpdatedPNR(Action):
    name: typing.ClassVar[str] = "end_and_retrieve_updated_pnr"
    description: typing.ClassVar[
        str
    ] = "Commit the changes to the PNR after the exchange details are confirmed and retrieve the updated PNR."

    @classmethod
    def required_slots(cls):
        return ["pnr_number"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        pnr_number = session.slots.get("pnr_number")
        if not pnr_number:
            logger.debug("PNR number not available.")
            await output_channel.send_text_message(
                "Cannot retrieve updated PNR without PNR number."
            )
            return [
                BotUttered(
                    text="Cannot retrieve updated PNR without PNR number.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for ending transaction and retrieving updated PNR
        logger.debug(f"Ending transaction and retrieving updated PNR for {pnr_number}.")
        updated_pnr_details = {"pnr_number": pnr_number, "status": "updated"}

        if updated_pnr_details:
            logger.debug("Updated PNR retrieved successfully.")
            return [
                SlotSet(
                    key="pnr_details",
                    value=updated_pnr_details,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        logger.debug("Failed to retrieve updated PNR.")
        await output_channel.send_text_message(
            "Failed to retrieve your updated booking details."
        )
        return [
            BotUttered(
                text="Failed to retrieve your updated booking details.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class TicketTheExchange(Action):
    name: typing.ClassVar[str] = "ticket_the_exchange"
    description: typing.ClassVar[
        str
    ] = "Issue the exchanged ticket based on the updated PNR information using AirTicketLLSRQ."

    @classmethod
    def required_slots(cls):
        return ["reissue_number"]

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        reissue_number = session.slots.get("reissue_number")
        if not reissue_number:
            logger.debug("Reissue number not available.")
            await output_channel.send_text_message(
                "Cannot issue ticket without a reissue number."
            )
            return [
                BotUttered(
                    text="Cannot issue ticket without a reissue number.",
                    data=None,
                    timestamp=time.time(),
                    metadata=None,
                )
            ]

        # Placeholder for actual ticketing
        logger.debug(f"Issuing ticket with reissue number {reissue_number}.")
        ticketing_success = True  # Assume success

        if ticketing_success:
            logger.debug("Ticket issued successfully.")
            return []

        logger.debug("Failed to issue ticket.")
        await output_channel.send_text_message("Failed to issue your ticket.")
        return [
            BotUttered(
                text="Failed to issue your ticket.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class CompletionConfirmation(Action):
    name: typing.ClassVar[str] = "completion_confirmation"
    description: typing.ClassVar[
        str
    ] = "Confirm the completion of the ticket exchange to the client."

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        message = "Your ticket exchange is complete. A confirmation email has been sent to you."
        await output_channel.send_text_message(message)
        return [
            BotUttered(
                text=message,
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]


class AskHumanConfirmation(Action):
    name: typing.ClassVar[str] = "ask_human_confirmation"
    description: typing.ClassVar[
        str
    ] = "Send a request to a human agent to review and approve the exchange before ticketing."

    async def run(
        self, output_channel: OutputChannel, session: Session
    ) -> typing.Optional[typing.List[Event]]:
        logger.debug("Requesting human agent approval.")
        # Placeholder for notifying human agent
        await output_channel.send_text_message(
            "Your exchange request is pending approval from a human agent."
        )
        return [
            BotUttered(
                text="Your exchange request is pending approval from a human agent.",
                data=None,
                timestamp=time.time(),
                metadata=None,
            )
        ]
