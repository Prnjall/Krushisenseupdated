import unittest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

from predictions.ai.gemini_provider import GeminiProvider
from predictions.ai.openai_provider import OpenAIProvider
from predictions.ai.errors import TransientAIError, PermanentAIError
from predictions.interoperability.schemas import VisionAdvisorySchema

class DummyClientError(Exception):
    def __init__(self, code, message="Error"):
        self.code = code
        self.message = message
        super().__init__(self.message)

class TestVisionProviders(unittest.TestCase):
    def setUp(self):
        self.schema = VisionAdvisorySchema.model_json_schema()
        self.image_bytes = b"dummy_image_data"
        self.mime_type = "image/jpeg"
        self.prompt_text = "Analyze this leaf."
        self.system_instruction = "You are an AI."

    # Gemini Tests
    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.gemini_provider.genai.Client")
    @patch("os.getenv")
    def test_gemini_vision_success(self, mock_getenv, mock_client, mock_generate):
        mock_getenv.return_value = "dummy_key"
        
        mock_response = MagicMock()
        mock_response.text = '{"assessment_type": "AI-Assisted Visual Assessment", "possible_condition": "Apple Scab", "confidence_level": "High", "visual_evidence": "Spots", "uncertainty_disclaimer": "Not a diagnosis", "recommended_next_step": "Consult expert"}'
        mock_generate.return_value = mock_response

        provider = GeminiProvider()
        result = provider.generate_vision_content(
            self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
        )

        self.assertEqual(result["possible_condition"], "Apple Scab")
        mock_generate.assert_called_once()
        args, kwargs = mock_generate.call_args
        contents = kwargs.get("contents")
        self.assertTrue(isinstance(contents, list))
        self.assertEqual(len(contents), 2)
        # Verify prompt text is in contents
        self.assertIn(self.prompt_text, contents)
        # Verify MIME type via Part object checking (it should be the first item)
        self.assertEqual(contents[0].inline_data.mime_type, self.mime_type)

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.gemini_provider.genai.Client")
    @patch("os.getenv")
    def test_gemini_vision_429(self, mock_getenv, mock_client, mock_generate):
        mock_getenv.return_value = "dummy_key"
        
        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            mock_generate.side_effect = DummyClientError(429, "Too Many Requests")
            
            provider = GeminiProvider()
            with self.assertRaises(TransientAIError):
                provider.generate_vision_content(
                    self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
                )

    @patch("predictions.ai.gemini_provider.generate_content_with_retry")
    @patch("predictions.ai.gemini_provider.genai.Client")
    @patch("os.getenv")
    def test_gemini_vision_permanent_error(self, mock_getenv, mock_client, mock_generate):
        mock_getenv.return_value = "dummy_key"
        
        with patch('predictions.ai.gemini_provider.ClientError', DummyClientError):
            mock_generate.side_effect = DummyClientError(400, "Bad Request")
            
            provider = GeminiProvider()
            with self.assertRaises(PermanentAIError):
                provider.generate_vision_content(
                    self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
                )

    # OpenAI Tests
    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_openai_vision_success(self, mock_getenv, mock_openai):
        mock_getenv.return_value = "dummy_key"
        
        mock_client_instance = MagicMock()
        mock_chat_response = MagicMock()
        mock_chat_response.choices[0].message.content = '{"assessment_type": "AI-Assisted Visual Assessment", "possible_condition": "Cedar Rust", "confidence_level": "Moderate", "visual_evidence": "Brown spots", "uncertainty_disclaimer": "Not a diagnosis", "recommended_next_step": "Consult expert"}'
        mock_client_instance.chat.completions.create.return_value = mock_chat_response
        mock_openai.return_value = mock_client_instance

        provider = OpenAIProvider()
        result = provider.generate_vision_content(
            self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
        )

        self.assertEqual(result["possible_condition"], "Cedar Rust")
        mock_client_instance.chat.completions.create.assert_called_once()
        args, kwargs = mock_client_instance.chat.completions.create.call_args
        messages = kwargs.get("messages")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertTrue(isinstance(messages[1]["content"], list))
        self.assertEqual(messages[1]["content"][0]["type"], "text")
        self.assertEqual(messages[1]["content"][1]["type"], "image_url")
        # Verify Base64 string is correctly formatted
        import base64
        b64_image = base64.b64encode(self.image_bytes).decode('utf-8')
        expected_url = f"data:{self.mime_type};base64,{b64_image}"
        self.assertEqual(messages[1]["content"][1]["image_url"]["url"], expected_url)

    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_openai_vision_transient_error(self, mock_getenv, mock_openai):
        mock_getenv.return_value = "dummy_key"
        
        mock_client_instance = MagicMock()
        import openai
        mock_client_instance.chat.completions.create.side_effect = openai.RateLimitError("Rate limit", response=MagicMock(), body=None)
        mock_openai.return_value = mock_client_instance

        provider = OpenAIProvider()
        with self.assertRaises(TransientAIError):
            provider.generate_vision_content(
                self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
            )

    @patch("predictions.ai.openai_provider.OpenAI")
    @patch("os.getenv")
    def test_openai_vision_permanent_error(self, mock_getenv, mock_openai):
        mock_getenv.return_value = "dummy_key"
        
        mock_client_instance = MagicMock()
        import openai
        mock_client_instance.chat.completions.create.side_effect = openai.BadRequestError("Bad request", response=MagicMock(), body=None)
        mock_openai.return_value = mock_client_instance

        provider = OpenAIProvider()
        with self.assertRaises(PermanentAIError):
            provider.generate_vision_content(
                self.prompt_text, self.image_bytes, self.mime_type, self.system_instruction, self.schema
            )
