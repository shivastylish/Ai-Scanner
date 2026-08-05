class AIScreenerError(Exception):
    """Base exception for AI Screener."""


class ProviderError(AIScreenerError):
    """Raised when a provider fails."""


class ValidationError(AIScreenerError):
    """Raised when data validation fails."""