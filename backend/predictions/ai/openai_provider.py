import json
import logging
import os
import copy
from typing import Any, Dict

import openai
from openai import OpenAI

from .interface import AIProvider
from .errors import TransientAIError, PermanentAIError, AIConfigurationError

logger = logging.getLogger(__name__)

def adapt_schema_for_openai(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively adapts a generic OpenAPI/JSON Schema for OpenAI Structured Outputs strict mode.
    OpenAI requires:
      - additionalProperties: False on all objects
      - All properties must be in the required list
    """
    adapted = copy.deepcopy(schema)

    if adapted.get("type") == "OBJECT" or adapted.get("type") == "object":
        adapted["type"] = "object"
        adapted["additionalProperties"] = False

        properties = adapted.get("properties", {})
        if properties:
            adapted_properties = {}
            for key, val in properties.items():
                adapted_properties[key] = adapt_schema_for_openai(val)
            adapted["properties"] = adapted_properties

            # OpenAI requires ALL properties to be listed as required
            adapted["required"] = list(properties.keys())

    elif adapted.get("type") == "ARRAY" or adapted.get("type") == "array":
        adapted["type"] = "array"
        if "items" in adapted:
            adapted["items"] = adapt_schema_for_openai(adapted["items"])

    elif adapted.get("type") in ["STRING", "string"]:
        adapted["type"] = "string"

    elif adapted.get("type") in ["NUMBER", "number"]:
        adapted["type"] = "number"

    elif adapted.get("type") in ["INTEGER", "integer"]:
        adapted["type"] = "integer"

    elif adapted.get("type") in ["BOOLEAN", "boolean"]:
        adapted["type"] = "boolean"

    return adapted

class OpenAIProvider(AIProvider):
    def __init__(self):
        self._model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def provider_name(self) -> str:
        return "OpenAI"

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
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured.")

        client = OpenAI(api_key=api_key)

        # Prepare OpenAI-specific JSON schema
        openai_schema = adapt_schema_for_openai(response_schema)

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "advisory_response",
                "schema": openai_schema,
                "strict": True
            }
        }

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt_text}
                ],
                response_format=response_format,
                temperature=temperature
            )

            content = response.choices[0].message.content
            advisory_data = json.loads(content)
            return advisory_data

        except openai.RateLimitError as e:
            logger.warning(f"OpenAI RateLimitError: {e}")
            raise TransientAIError(f"OpenAI rate limit: {e}") from e
        except openai.APIConnectionError as e:
            logger.warning(f"OpenAI APIConnectionError: {e}")
            raise TransientAIError(f"OpenAI connection error: {e}") from e
        except openai.InternalServerError as e:
            logger.warning(f"OpenAI InternalServerError: {e}")
            raise TransientAIError(f"OpenAI server error: {e}") from e
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI AuthenticationError: {e}")
            raise PermanentAIError(f"OpenAI auth error: {e}") from e
        except openai.BadRequestError as e:
            logger.error(f"OpenAI BadRequestError: {e}")
            raise PermanentAIError(f"OpenAI bad request: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI returned invalid JSON: {e}")
            raise TransientAIError(f"OpenAI returned malformed data: {e}") from e
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}")
            raise PermanentAIError(f"OpenAI unexpected error: {e}") from e

    def generate_vision_content(
        self,
        prompt_text: str,
        image_bytes: bytes,
        mime_type: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        import base64
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured.")

        client = OpenAI(api_key=api_key)

        openai_schema = adapt_schema_for_openai(response_schema)

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "vision_advisory_response",
                "schema": openai_schema,
                "strict": True
            }
        }

        try:
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            image_url = f"data:{mime_type};base64,{b64_image}"

            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]}
                ],
                response_format=response_format,
                temperature=temperature
            )

            content = response.choices[0].message.content
            advisory_data = json.loads(content)
            return advisory_data

        except openai.RateLimitError as e:
            logger.warning(f"OpenAI Vision RateLimitError: {e}")
            raise TransientAIError(f"OpenAI vision rate limit: {e}") from e
        except openai.APIConnectionError as e:
            logger.warning(f"OpenAI Vision APIConnectionError: {e}")
            raise TransientAIError(f"OpenAI vision connection error: {e}") from e
        except openai.InternalServerError as e:
            logger.warning(f"OpenAI Vision InternalServerError: {e}")
            raise TransientAIError(f"OpenAI vision server error: {e}") from e
        except openai.AuthenticationError as e:
            logger.error(f"OpenAI Vision AuthenticationError: {e}")
            raise PermanentAIError(f"OpenAI vision auth error: {e}") from e
        except openai.BadRequestError as e:
            logger.error(f"OpenAI Vision BadRequestError: {e}")
            raise PermanentAIError(f"OpenAI vision bad request: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"OpenAI Vision returned invalid JSON: {e}")
            raise TransientAIError(f"OpenAI vision returned malformed data: {e}") from e
        except Exception as e:
            logger.error(f"OpenAI Vision unexpected error: {e}")
            raise PermanentAIError(f"OpenAI vision unexpected error: {e}") from e
