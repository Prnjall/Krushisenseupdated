import json
import logging
import os
from typing import Any, Dict

from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

from .interface import AIProvider
from .errors import TransientAIError, PermanentAIError, AIConfigurationError
from predictions.gemini_utils import generate_content_with_retry

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self):
        self._model = 'gemini-3.6-flash'

    @property
    def provider_name(self) -> str:
        return "Google Gemini"

    @property
    def model_version(self) -> str:
        return self._model

    def generate_advisory(
        self,
        prompt_text: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AIConfigurationError("GEMINI_API_KEY is not configured.")

        client = genai.Client(api_key=api_key)

        try:
            response = generate_content_with_retry(
                client=client,
                model=self._model,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=temperature,
                ),
            )

            advisory_data = json.loads(response.text)
            return advisory_data

        except ServerError as e:
            # 500, 503, 504 are usually ServerErrors
            logger.warning(f"Gemini ServerError: {e}")
            raise TransientAIError(f"Gemini service unavailable: {e}") from e
        except ClientError as e:
            # Check for 429 RESOURCE_EXHAUSTED specifically
            if getattr(e, 'code', None) == 429:
                logger.warning(f"Gemini quota exhausted (429): {e}")
                raise TransientAIError(f"Gemini quota exhausted: {e}") from e
            # 400 (Bad Request), 403, 401
            logger.error(f"Gemini ClientError: {e}")
            raise PermanentAIError(f"Gemini client error: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            raise TransientAIError(f"Gemini returned malformed data: {e}") from e
        except Exception as e:
            # Check for connection errors, timeouts, etc.
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                logger.warning(f"Gemini connection issue: {e}")
                raise TransientAIError(f"Gemini connection failed: {e}") from e

            # Default to permanent error for unknown exceptions to prevent fallback loops
            logger.error(f"Gemini unexpected error: {e}")
            raise PermanentAIError(f"Gemini unexpected error: {e}") from e

    def generate_vision_content(
        self,
        prompt_text: str,
        image_bytes: bytes,
        mime_type: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise AIConfigurationError("GEMINI_API_KEY is not configured.")

        client = genai.Client(api_key=api_key)

        try:
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            response = generate_content_with_retry(
                client=client,
                model=self._model,
                contents=[image_part, prompt_text],
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    temperature=temperature,
                ),
            )

            advisory_data = json.loads(response.text)
            return advisory_data

        except ServerError as e:
            logger.warning(f"Gemini Vision ServerError: {e}")
            raise TransientAIError(f"Gemini vision service unavailable: {e}") from e
        except ClientError as e:
            if getattr(e, 'code', None) == 429:
                logger.warning(f"Gemini Vision quota exhausted (429): {e}")
                raise TransientAIError(f"Gemini vision quota exhausted: {e}") from e
            logger.error(f"Gemini Vision ClientError: {e}")
            raise PermanentAIError(f"Gemini vision client error: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Gemini Vision returned invalid JSON: {e}")
            raise TransientAIError(f"Gemini vision returned malformed data: {e}") from e
        except Exception as e:
            error_str = str(e).lower()
            if "timeout" in error_str or "connection" in error_str:
                logger.warning(f"Gemini Vision connection issue: {e}")
                raise TransientAIError(f"Gemini vision connection failed: {e}") from e
            logger.error(f"Gemini Vision unexpected error: {e}")
            raise PermanentAIError(f"Gemini vision unexpected error: {e}") from e
