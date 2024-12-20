from typing import Dict, Type
import logging

from .base import FlightProvider
from .sabre import SabreClient
from ..models import UnknownProviderError

logger = logging.getLogger(__name__)


class FlightProviderFactory:
    """Factory for creating flight provider instances"""

    _providers: Dict[str, Type[FlightProvider]] = {"sabre": SabreClient}

    @classmethod
    def create(cls, provider_type: str, **config) -> FlightProvider:
        """Create a new flight provider instance

        Args:
            provider_type: Type of provider to create (e.g. "sabre")
            **config: Provider-specific configuration

        Returns:
            FlightProvider instance

        Raises:
            UnknownProviderError: If provider type is not supported
        """
        provider_cls = cls._providers.get(provider_type.lower())
        if not provider_cls:
            raise UnknownProviderError(f"Unknown provider type: {provider_type}")

        return provider_cls(**config)

    @classmethod
    def register_provider(cls, name: str, provider_cls: Type[FlightProvider]):
        """Register a new provider type

        Args:
            name: Name to register the provider under
            provider_cls: Provider class to register
        """
        cls._providers[name.lower()] = provider_cls
