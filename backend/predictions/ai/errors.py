from typing import Any, Dict

class TransientAIError(Exception):
    """Raised for retryable/fallback infrastructure errors (e.g. 503, 500, timeouts)."""
    pass

class PermanentAIError(Exception):
    """Raised for non-retryable errors (e.g. 400 Bad Request, safety rejection)."""
    pass

class AIConfigurationError(Exception):
    """Raised when provider configuration is missing or invalid."""
    pass
