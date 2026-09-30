import pytest
from unittest.mock import patch, MagicMock
from predictions.ai.orchestrator import AIOrchestrator
from predictions.ai.errors import TransientAIError, PermanentAIError, AIConfigurationError

@pytest.fixture
def orchestrator():
    return AIOrchestrator()

def test_primary_succeeds_no_fallback(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.return_value = {"advice": "Primary"}
        
        advisory, metadata = orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        assert advisory == {"advice": "Primary"}
        assert metadata["provider"] == "Google Gemini"
        mock_primary.assert_called_once()
        mock_backup.assert_not_called()
        mock_openai.assert_not_called()

def test_primary_429_backup_succeeds(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.side_effect = TransientAIError("Quota exceeded (429)")
        mock_backup.return_value = {"advice": "Backup"}
        
        advisory, metadata = orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        assert advisory == {"advice": "Backup"}
        assert metadata["provider"] == "Google Gemini (Backup)"
        mock_primary.assert_called_once()
        mock_backup.assert_called_once()
        mock_openai.assert_not_called()

def test_primary_429_backup_fails_openai_called(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.side_effect = TransientAIError("Quota exceeded")
        mock_backup.side_effect = TransientAIError("Backup Quota exceeded")
        mock_openai.return_value = {"advice": "OpenAI"}
        
        advisory, metadata = orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        assert advisory == {"advice": "OpenAI"}
        assert metadata["provider"] == "OpenAI"
        mock_primary.assert_called_once()
        mock_backup.assert_called_once()
        mock_openai.assert_called_once()

def test_primary_permanent_error(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.side_effect = PermanentAIError("Invalid Request")
        
        with pytest.raises(PermanentAIError):
            orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        mock_primary.assert_called_once()
        mock_backup.assert_not_called()
        mock_openai.assert_not_called()

def test_backup_key_missing(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.side_effect = TransientAIError("Quota exceeded")
        mock_backup.side_effect = AIConfigurationError("Key missing")
        mock_openai.return_value = {"advice": "OpenAI"}
        
        advisory, metadata = orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        assert advisory == {"advice": "OpenAI"}
        mock_primary.assert_called_once()
        mock_backup.assert_called_once()
        mock_openai.assert_called_once()

def test_all_fail(orchestrator):
    with patch.object(orchestrator.gemini, 'generate_advisory') as mock_primary, \
         patch.object(orchestrator.gemini_backup, 'generate_advisory') as mock_backup, \
         patch.object(orchestrator.openai, 'generate_advisory') as mock_openai:
        
        mock_primary.side_effect = TransientAIError("Error")
        mock_backup.side_effect = TransientAIError("Error")
        mock_openai.side_effect = TransientAIError("Error")
        
        with pytest.raises(TransientAIError, match="All AI providers unavailable"):
            orchestrator.generate_advisory_with_fallback("prompt", "sys", {})
        
        mock_primary.assert_called_once()
        mock_backup.assert_called_once()
        mock_openai.assert_called_once()
