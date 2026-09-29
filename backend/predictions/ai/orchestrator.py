import logging
import os
from typing import Any, Dict, Tuple

from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .errors import TransientAIError, PermanentAIError, AIConfigurationError

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.gemini = GeminiProvider()
        self.openai = OpenAIProvider()

    def generate_advisory_with_fallback(
        self,
        prompt_text: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Attempts to generate an advisory using the primary provider (Gemini).
        If it encounters a TransientAIError, falls back to OpenAI.

        Returns a tuple of:
          - The generated parsed JSON dictionary matching the schema.
          - Metadata about the provider used (for provenance).
        """
        # 1. Primary Attempt (Gemini)
        # Note: GeminiProvider itself handles internal retries for 503 via gemini_utils
        try:
            advisory = self.gemini.generate_advisory(
                prompt_text, system_instruction, response_schema, temperature
            )
            metadata = {
                "provider": self.gemini.provider_name,
                "model_version": self.gemini.model_version
            }
            return advisory, metadata
        except TransientAIError as e:
            logger.warning(f"[AI Orchestrator] Primary provider transient failure: {e}. Attempting fallback.")
        except PermanentAIError as e:
            logger.error(f"[AI Orchestrator] Primary provider permanent failure: {e}. Skipping fallback.")
            raise
        except AIConfigurationError as e:
            logger.error(f"[AI Orchestrator] Primary provider misconfigured: {e}. Skipping fallback.")
            raise

        # 2. Fallback Attempt (OpenAI)
        try:
            advisory = self.openai.generate_advisory(
                prompt_text, system_instruction, response_schema, temperature
            )
            metadata = {
                "provider": self.openai.provider_name,
                "model_version": self.openai.model_version
            }
            logger.info("[AI Orchestrator] Fallback provider succeeded.")
            return advisory, metadata
        except AIConfigurationError as e:
            logger.warning(f"[AI Orchestrator] Fallback provider not configured ({e}). Returning primary failure.")
            # If fallback is misconfigured (e.g. no key), we consider the AI service unavailable
            raise TransientAIError("All AI providers unavailable.") from e
        except TransientAIError as e:
            logger.error(f"[AI Orchestrator] Fallback provider transient failure: {e}.")
            raise TransientAIError("All AI providers unavailable.") from e
        except PermanentAIError as e:
            logger.error(f"[AI Orchestrator] Fallback provider permanent failure: {e}.")
            raise

    def generate_vision_advisory_with_fallback(
        self,
        prompt_text: str,
        image_bytes: bytes,
        mime_type: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Attempts to generate a vision advisory using the primary provider (Gemini).
        If it encounters a TransientAIError, falls back to OpenAI.

        Returns a tuple of:
          - The generated parsed JSON dictionary matching the schema.
          - Metadata about the provider used (for provenance).
        """
        # 1. Primary Attempt (Gemini)
        try:
            advisory = self.gemini.generate_vision_content(
                prompt_text, image_bytes, mime_type, system_instruction, response_schema, temperature
            )
            metadata = {
                "provider": self.gemini.provider_name,
                "model_version": self.gemini.model_version
            }
            return advisory, metadata
        except TransientAIError as e:
            logger.warning(f"[AI Orchestrator] Primary vision provider transient failure: {e}. Attempting fallback.")
        except PermanentAIError as e:
            logger.error(f"[AI Orchestrator] Primary vision provider permanent failure: {e}. Skipping fallback.")
            raise
        except AIConfigurationError as e:
            logger.error(f"[AI Orchestrator] Primary vision provider misconfigured: {e}. Skipping fallback.")
            raise

        # 2. Fallback Attempt (OpenAI)
        try:
            advisory = self.openai.generate_vision_content(
                prompt_text, image_bytes, mime_type, system_instruction, response_schema, temperature
            )
            metadata = {
                "provider": self.openai.provider_name,
                "model_version": self.openai.model_version
            }
            logger.info("[AI Orchestrator] Fallback vision provider succeeded.")
            return advisory, metadata
        except AIConfigurationError as e:
            logger.warning(f"[AI Orchestrator] Fallback vision provider not configured ({e}). Returning primary failure.")
            raise TransientAIError("All AI vision providers unavailable.") from e
        except TransientAIError as e:
            logger.error(f"[AI Orchestrator] Fallback vision provider transient failure: {e}.")
            raise TransientAIError("All AI vision providers unavailable.") from e
        except PermanentAIError as e:
            logger.error(f"[AI Orchestrator] Fallback vision provider permanent failure: {e}.")
            raise
