from abc import ABC, abstractmethod
from typing import Optional

from ..models import Reservation


class FlightProvider(ABC):
    """Base class for flight providers"""

    @abstractmethod
    async def get_reservation(self, pnr: str) -> Optional[Reservation]:
        """Retrieve a reservation by PNR

        Args:
            pnr: The PNR locator to retrieve

        Returns:
            Reservation object if found, None otherwise

        Raises:
            ConnectionError: If the request fails
        """

    @abstractmethod
    async def get_flight_rules(self, ticket_number: str) -> Optional[str]:
        """Retrieve flight fare rules for a ticket

        Args:
            ticket_number: The ticket number to get rules for

        Returns:
            Fare rules text if found, None otherwise

        Raises:
            ConnectionError: If the request fails
        """
