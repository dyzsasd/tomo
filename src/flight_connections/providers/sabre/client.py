from datetime import datetime
import logging
from typing import Dict, Optional
import xml.etree.ElementTree as ET
import requests

from ...models import (
    Reservation,
    Passenger,
    PassengerType,
    FlightSegment,
    Ticket,
    ProviderConnectionError,
)

from ..base import FlightProvider

logger = logging.getLogger(__name__)


class SabreClient(FlightProvider):
    """Client for connecting to Sabre APIs"""

    def __init__(self, endpoint: str, username: str, password: str, pcc: str):
        """Initialize Sabre client

        Args:
            endpoint: Sabre API endpoint URL
            username: API username
            password: API password
            pcc: Pseudo City Code
        """
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.pcc = pcc
        self._session_token = None

    def _get_soap_headers(self) -> Dict:
        """Get SOAP headers for requests"""
        if not self._session_token:
            # TODO: Implement session token retrieval
            pass

        return {"Content-Type": "text/xml", "SOAPAction": "GetReservationRQ"}

    def _build_get_reservation_request(self, pnr: str) -> str:
        """Build GetReservationRQ SOAP request

        Args:
            pnr: The PNR to retrieve

        Returns:
            SOAP request XML as string
        """
        return f"""<?xml version="1.0"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                         xmlns:eb="http://www.ebxml.org/namespaces/messageHeader"
                         xmlns:wsse="http://schemas.xmlsoap.org/ws/2002/12/secext">
            <soapenv:Header>
                <eb:MessageHeader soapenv:mustUnderstand="1" eb:version="2.0">
                    <eb:ConversationId>{datetime.now().isoformat()}</eb:ConversationId>
                    <eb:From>
                        <eb:PartyId type="urn:x12.org:IO5:01">{self.pcc}</eb:PartyId>
                    </eb:From>
                    <eb:To>
                        <eb:PartyId type="urn:x12.org:IO5:01">webservices.sabre.com</eb:PartyId>
                    </eb:To>
                    <eb:CPAId>{self.pcc}</eb:CPAId>
                    <eb:Service eb:type="OTA"/>
                    <eb:Action>GetReservationRQ</eb:Action>
                </eb:MessageHeader>
                <wsse:Security>
                    <wsse:BinarySecurityToken>{self._session_token}</wsse:BinarySecurityToken>
                </wsse:Security>
            </soapenv:Header>
            <soapenv:Body>
                <GetReservationRQ Version="1.19.0" xmlns="http://webservices.sabre.com/pnrbuilder/v1_19">
                    <Locator>{pnr}</Locator>
                    <RequestType>Stateful</RequestType>
                    <ReturnOptions>
                        <SubjectAreas>
                            <SubjectArea>ITINERARY</SubjectArea>
                            <SubjectArea>PRICE_QUOTE</SubjectArea>
                            <SubjectArea>TICKETING</SubjectArea>
                        </SubjectAreas>
                        <ViewName>Full</ViewName>
                        <ResponseFormat>STL</ResponseFormat>
                    </ReturnOptions>
                </GetReservationRQ>
            </soapenv:Body>
        </soapenv:Envelope>"""

    def _parse_reservation_response(self, response_xml: str) -> Reservation:
        """Parse GetReservationRS response into Reservation model

        Args:
            response_xml: Response XML from Sabre

        Returns:
            Reservation object

        Raises:
            ProviderConnectionError: If response parsing fails
        """
        try:
            root = ET.fromstring(response_xml)

            # Parse basic PNR info
            res_elem = root.find(
                ".//stl19:Reservation",
                {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
            )

            # Parse passengers
            passengers = []
            for pax_elem in res_elem.findall(
                ".//stl19:Passenger",
                {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
            ):
                pax = Passenger(
                    last_name=pax_elem.find(
                        "stl19:LastName",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    first_name=pax_elem.find(
                        "stl19:FirstName",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    passenger_type=PassengerType(pax_elem.get("passengerType")),
                )
                passengers.append(pax)

            # Parse flight segments
            segments = []
            for seg_elem in res_elem.findall(
                ".//stl19:Segment",
                {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
            ):
                flight = FlightSegment(
                    departure_airport=seg_elem.find(
                        ".//stl19:DepartureAirport",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    arrival_airport=seg_elem.find(
                        ".//stl19:ArrivalAirport",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    departure_time=datetime.fromisoformat(
                        seg_elem.find(
                            ".//stl19:DepartureDateTime",
                            {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                        ).text
                    ),
                    arrival_time=datetime.fromisoformat(
                        seg_elem.find(
                            ".//stl19:ArrivalDateTime",
                            {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                        ).text
                    ),
                    marketing_carrier=seg_elem.find(
                        ".//stl19:MarketingCarrier",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    flight_number=seg_elem.find(
                        ".//stl19:FlightNumber",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    booking_class=seg_elem.find(
                        ".//stl19:BookingClass",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    status=seg_elem.find(
                        ".//stl19:Status",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                )
                segments.append(flight)

            # Parse tickets if present
            tickets = []
            for tkt_elem in res_elem.findall(
                ".//stl19:Ticket",
                {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
            ):
                ticket = Ticket(
                    ticket_number=tkt_elem.find(
                        ".//stl19:TicketNumber",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                    issue_date=datetime.fromisoformat(
                        tkt_elem.find(
                            ".//stl19:IssueDate",
                            {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                        ).text
                    ),
                    passenger=next(
                        p
                        for p in passengers
                        if p.last_name
                        == tkt_elem.find(
                            ".//stl19:PassengerName",
                            {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                        ).text.split()[0]
                    ),
                    amount=float(
                        tkt_elem.find(
                            ".//stl19:Amount",
                            {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                        ).text
                    ),
                    currency=tkt_elem.find(
                        ".//stl19:Currency",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text,
                )
                tickets.append(ticket)

            # Create reservation
            return Reservation(
                pnr=res_elem.find(
                    ".//stl19:RecordLocator",
                    {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                ).text,
                creation_date=datetime.fromisoformat(
                    res_elem.find(
                        ".//stl19:CreateDateTime",
                        {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                    ).text
                ),
                passengers=passengers,
                segments=segments,
                tickets=tickets,
                status=res_elem.find(
                    ".//stl19:Status",
                    {"stl19": "http://webservices.sabre.com/pnrbuilder/v1_19"},
                ).text,
                agency_iata=self.pcc,
            )

        except Exception as e:
            logger.error(f"Failed to parse Sabre response: {e}")
            raise ProviderConnectionError(f"Failed to parse Sabre response: {e}") from e

    async def get_reservation(self, pnr: str) -> Optional[Reservation]:
        """Retrieve a reservation by PNR

        Args:
            pnr: The PNR to retrieve

        Returns:
            Reservation object if found, None otherwise

        Raises:
            ProviderConnectionError: If the request fails
        """
        try:
            request_xml = self._build_get_reservation_request(pnr)

            response = requests.post(
                self.endpoint, headers=self._get_soap_headers(), data=request_xml
            )

            if response.status_code != 200:
                logger.error(f"Sabre request failed with status {response.status_code}")
                raise ProviderConnectionError(
                    f"Sabre request failed with status {response.status_code}"
                )

            return self._parse_reservation_response(response.text)

        except requests.RequestException as e:
            logger.error(f"Failed to connect to Sabre: {e}")
            raise ProviderConnectionError(f"Failed to connect to Sabre: {e}") from e
