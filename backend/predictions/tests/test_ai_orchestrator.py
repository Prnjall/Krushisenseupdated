import json
import unittest
from unittest.mock import patch, MagicMock
from google.genai.errors import ServerError, ClientError
import openai
from pydantic import BaseModel

from predictions.ai.orchestrator import AIOrchestrator
from predictions.ai.errors import TransientAIError, PermanentAIError, AIConfigurationError
from predictions.ai.openai_provider import adapt_schema_for_openai

class DummyServerError(Exception):
    def __init__(self, code):
        self.code = code

class DummyClientError(Exception):
    def __init__(self, code):
        self.code = code

class TestAIOrchestrator(unittest.TestCase):
    def setUp(self):
        self.response_schema = {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING"}
            },
            "required": ["summary"]
        }

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_gemini_success(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        mock_response = MagicMock()
        mock_response.text = '{"summary": "Test summary"}'
        mock_gemini_generate.return_value = mock_response

        orchestrator = AIOrchestrator()
        advisory, metadata = orchestrator.generate_advisory_with_fallback(
            prompt_text="test", system_instruction="test", response_schema=self.response_schema
        )

        self.assertEqual(advisory["summary"], "Test summary")
        self.assertEqual(metadata["provider"], "Google Gemini")
        mock_gemini_generate.assert_called_once()
        mock_openai.assert_not_called()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_gemini_transient_fallback_to_openai(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        import predictions.ai.gemini_provider

        # Gemini raises 503
        with patch('predictions.ai.gemini_provider.ServerError', DummyServerError):
            mock_gemini_generate.side_effect = DummyServerError(503)

            # OpenAI succeeds
            mock_openai_client = MagicMock()
            mock_chat_response = MagicMock()
            mock_chat_response.choices[0].message.content = '{"summary": "OpenAI summary"}'
            mock_openai_client.chat.completions.create.return_value = mock_chat_response
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            advisory, metadata = orchestrator.generate_advisory_with_fallback(
                prompt_text="test", system_instruction="test", response_schema=self.response_schema
            )

            self.assertEqual(advisory["summary"], "OpenAI summary")
            self.assertEqual(metadata["provider"], "OpenAI")
            # generate_content_with_retry is patched globally, so it is called once by primary
            # and once by backup (both are GeminiProvider instances sharing the same mock).
            # Each provider makes exactly ONE underlying API call — no retry.
            self.assertEqual(mock_gemini_generate.call_count, 2)
            mock_openai.assert_called_once()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_gemini_permanent_error_no_fallback(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            # Gemini raises 400 ClientError
            mock_gemini_generate.side_effect = DummyClientError(400)

            orchestrator = AIOrchestrator()
            with self.assertRaises(PermanentAIError):
                orchestrator.generate_advisory_with_fallback(
                    prompt_text="test", system_instruction="test", response_schema=self.response_schema
                )

            mock_gemini_generate.assert_called_once()
            mock_openai.assert_not_called()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_gemini_429_fallback_to_openai(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            # Gemini raises 429 ClientError
            mock_gemini_generate.side_effect = DummyClientError(429)

            # OpenAI succeeds
            mock_openai_client = MagicMock()
            mock_chat_response = MagicMock()
            mock_chat_response.choices[0].message.content = '{"summary": "OpenAI summary"}'
            mock_openai_client.chat.completions.create.return_value = mock_chat_response
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            advisory, metadata = orchestrator.generate_advisory_with_fallback(
                prompt_text="test", system_instruction="test", response_schema=self.response_schema
            )

            self.assertEqual(advisory["summary"], "OpenAI summary")
            self.assertEqual(metadata["provider"], "OpenAI")
            # Same global mock: called once by primary, once by backup. Total = 2.
            self.assertEqual(mock_gemini_generate.call_count, 2)
            mock_openai.assert_called_once()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_both_providers_fail(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ServerError', DummyServerError):
            mock_gemini_generate.side_effect = DummyServerError(503)

            mock_openai_client = MagicMock()
            mock_openai_client.chat.completions.create.side_effect = openai.InternalServerError("500", response=MagicMock(), body=None)
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            with self.assertRaises(TransientAIError):
                orchestrator.generate_advisory_with_fallback(
                    prompt_text="test", system_instruction="test", response_schema=self.response_schema
                )

    def test_schema_conversion(self):
        gemini_schema = {
            "type": "OBJECT",
            "properties": {
                "field1": {"type": "STRING"},
                "field2": {
                    "type": "ARRAY",
                    "items": {"type": "NUMBER"}
                }
            },
            "required": ["field1"]
        }

        openai_schema = adapt_schema_for_openai(gemini_schema)

        self.assertEqual(openai_schema["type"], "object")
        self.assertEqual(openai_schema["additionalProperties"], False)
        self.assertEqual(openai_schema["properties"]["field1"]["type"], "string")
        self.assertEqual(openai_schema["properties"]["field2"]["type"], "array")
        self.assertEqual(openai_schema["properties"]["field2"]["items"]["type"], "number")

        # OpenAI requires ALL properties to be required
        self.assertIn("field1", openai_schema["required"])
        self.assertIn("field2", openai_schema["required"])


    # --- Vision Fallback Tests ---
    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_gemini_success(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        mock_response = MagicMock()
        mock_response.text = '{"summary": "Test vision summary"}'
        mock_gemini_generate.return_value = mock_response

        orchestrator = AIOrchestrator()
        advisory, metadata = orchestrator.generate_vision_advisory_with_fallback(
            prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
        )

        self.assertEqual(advisory["summary"], "Test vision summary")
        self.assertEqual(metadata["provider"], "Google Gemini")
        mock_gemini_generate.assert_called_once()
        mock_openai.assert_not_called()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_gemini_429_fallback_to_openai(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            mock_gemini_generate.side_effect = DummyClientError(429)

            mock_openai_client = MagicMock()
            mock_chat_response = MagicMock()
            mock_chat_response.choices[0].message.content = '{"summary": "OpenAI vision summary"}'
            mock_openai_client.chat.completions.create.return_value = mock_chat_response
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            advisory, metadata = orchestrator.generate_vision_advisory_with_fallback(
                prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
            )

            self.assertEqual(advisory["summary"], "OpenAI vision summary")
            self.assertEqual(metadata["provider"], "OpenAI")
            self.assertEqual(mock_gemini_generate.call_count, 2)
            mock_openai.assert_called_once()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_gemini_503_fallback_to_openai(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ServerError', DummyServerError):
            mock_gemini_generate.side_effect = DummyServerError(503)

            mock_openai_client = MagicMock()
            mock_chat_response = MagicMock()
            mock_chat_response.choices[0].message.content = '{"summary": "OpenAI vision summary"}'
            mock_openai_client.chat.completions.create.return_value = mock_chat_response
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            advisory, metadata = orchestrator.generate_vision_advisory_with_fallback(
                prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
            )

            self.assertEqual(advisory["summary"], "OpenAI vision summary")
            self.assertEqual(metadata["provider"], "OpenAI")
            self.assertEqual(mock_gemini_generate.call_count, 2)
            mock_openai.assert_called_once()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_gemini_permanent_error(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            mock_gemini_generate.side_effect = DummyClientError(400)

            orchestrator = AIOrchestrator()
            with self.assertRaises(PermanentAIError):
                orchestrator.generate_vision_advisory_with_fallback(
                    prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
                )

            mock_gemini_generate.assert_called_once()
            mock_openai.assert_not_called()

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_both_providers_fail_transient(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ServerError', DummyServerError):
            mock_gemini_generate.side_effect = DummyServerError(503)

            mock_openai_client = MagicMock()
            mock_openai_client.chat.completions.create.side_effect = openai.InternalServerError("500", response=MagicMock(), body=None)
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            with self.assertRaises(TransientAIError):
                orchestrator.generate_vision_advisory_with_fallback(
                    prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
                )

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_vision_both_providers_fail_permanent(self, mock_getenv, mock_openai, mock_gemini_generate):
        mock_getenv.side_effect = lambda key, default=None: "dummy_key" if "API_KEY" in key else default

        with patch('predictions.ai.gemini_provider.ServerError', DummyServerError):
            mock_gemini_generate.side_effect = DummyServerError(503)

            mock_openai_client = MagicMock()
            mock_openai_client.chat.completions.create.side_effect = openai.BadRequestError("400", response=MagicMock(), body=None)
            mock_openai.return_value = mock_openai_client

            orchestrator = AIOrchestrator()
            with self.assertRaises(PermanentAIError):
                orchestrator.generate_vision_advisory_with_fallback(
                    prompt_text="test", image_bytes=b"dummy", mime_type="image/jpeg", system_instruction="test", response_schema=self.response_schema
                )
