from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class PassengerType(str, Enum):
    ADULT = "ADT"
    CHILD = "CHD"
    INFANT = "INF"


class Passenger(BaseModel):
    """Passenger information"""

    last_name: str
    first_name: str
    passenger_type: PassengerType
    date_of_birth: Optional[datetime] = None
    document_number: Optional[str] = None


class FlightSegment(BaseModel):
    """Flight segment information"""

    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    marketing_carrier: str
    operating_carrier: Optional[str] = None
    flight_number: str
    booking_class: str
    status: str


class FareComponent(BaseModel):
    """Fare component information"""

    fare_basis: str
    passenger_type: PassengerType
    amount: float
    currency: str


class Ticket(BaseModel):
    """Ticket information"""

    ticket_number: str
    passenger: Passenger
    issue_date: datetime
    amount: float
    currency: str


class Reservation(BaseModel):
    """Core reservation model"""

    pnr: str
    creation_date: datetime
    passengers: List[Passenger]
    segments: List[FlightSegment]
    tickets: Optional[List[Ticket]] = None
    status: str
    agency_iata: Optional[str] = None
