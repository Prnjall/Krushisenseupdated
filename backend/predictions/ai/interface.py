from abc import ABC, abstractmethod
from typing import Any, Dict

class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the AI provider."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Return the underlying model version used."""
        pass

    @abstractmethod
    def generate_advisory(
        self,
        prompt_text: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generates an advisory matching the given OpenAPI response_schema dictionary.
        Raises TransientAIError on infrastructure issues.
        Raises PermanentAIError on fatal prompt/schema/auth issues.
        Raises AIConfigurationError if misconfigured.
        """
        pass

    @abstractmethod
    def generate_vision_content(
        self,
        prompt_text: str,
        image_bytes: bytes,
        mime_type: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Generates a multimodal advisory.
        Raises TransientAIError on infrastructure issues.
        Raises PermanentAIError on fatal prompt/schema/auth issues.
        Raises AIConfigurationError if misconfigured.
        """
        pass
