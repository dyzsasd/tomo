class ProviderConnectionError(Exception):
    """Base exception for connection errors"""


class AuthenticationError(ProviderConnectionError):
    """Authentication related errors"""


class UnknownProviderError(ProviderConnectionError):
    """Unknown provider errors"""
