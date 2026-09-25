import pytest
from unittest.mock import MagicMock, patch
from google.genai.errors import ServerError
from predictions.gemini_utils import generate_content_with_retry

class MockResponse:
    def __init__(self, text="mock"):
        self.text = text

def create_mock_server_error(code):
    return ServerError(code, "Mock Error", None)

def test_successful_first_request():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = MockResponse("success")

    res = generate_content_with_retry(mock_client, "model", "contents")
    assert res.text == "success"
    assert mock_client.models.generate_content.call_count == 1

@patch("predictions.gemini_utils.time.sleep")
def test_503_followed_by_success(mock_sleep):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        create_mock_server_error(503),
        MockResponse("success_on_retry")
    ]

    res = generate_content_with_retry(mock_client, "model", "contents")
    assert res.text == "success_on_retry"
    assert mock_client.models.generate_content.call_count == 2
    mock_sleep.assert_called_once()

@patch("predictions.gemini_utils.time.sleep")
def test_repeated_503_stops_after_max_attempts(mock_sleep):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        create_mock_server_error(503),
        create_mock_server_error(503),
        create_mock_server_error(503),
        create_mock_server_error(503)
    ]

    with pytest.raises(ServerError) as exc_info:
        generate_content_with_retry(mock_client, "model", "contents", max_attempts=3)

    assert exc_info.value.code == 503
    assert mock_client.models.generate_content.call_count == 3
    assert mock_sleep.call_count == 2

@patch("predictions.gemini_utils.time.sleep")
def test_non_503_exception_is_not_retried(mock_sleep):
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = create_mock_server_error(400)

    with pytest.raises(ServerError) as exc_info:
        generate_content_with_retry(mock_client, "model", "contents")

    assert exc_info.value.code == 400
    assert mock_client.models.generate_content.call_count == 1
    mock_sleep.assert_not_called()
