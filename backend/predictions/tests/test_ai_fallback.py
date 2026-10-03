"""
Quota-safety tests for the KrushiSense AI provider chain.

IMPORTANT: No real API calls are made in any of these tests.
All provider behaviour is exercised through mocks only.

Tests verify:
- Each provider is called AT MOST ONCE per advisory request.
- No provider-level retry occurs (provider raises immediately on transient error).
- The orchestrator fallback chain works correctly in all combinations.
- Permanent errors skip fallback as designed.
- All 10 required scenarios are covered.
"""

import pytest
from unittest.mock import patch, MagicMock

from predictions.ai.orchestrator import AIOrchestrator
from predictions.ai.errors import TransientAIError, PermanentAIError, AIConfigurationError
from predictions.gemini_utils import generate_content_with_retry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SCHEMA = {
    "type": "OBJECT",
    "properties": {"summary": {"type": "STRING"}},
    "required": ["summary"],
}
CALL_ARGS = ("prompt", "system_instruction", SCHEMA)


def _ok(msg="Advisory OK"):
    return {"summary": msg}


def _orch():
    """Return a fresh AIOrchestrator (no real credentials needed; providers mocked)."""
    return AIOrchestrator()


# ===========================================================================
# TEST 1 - Primary Gemini succeeds
# ===========================================================================

def test_01_primary_succeeds_no_backup_no_openai():
    """Primary=1, Backup=0, OpenAI=0. Returns advisory."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory", return_value=_ok("Primary")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory") as p2, \
         patch.object(o.openai, "generate_advisory") as p3:

        advisory, meta = o.generate_advisory_with_fallback(*CALL_ARGS)

    assert advisory == _ok("Primary")
    assert meta["provider"] == "Google Gemini"
    p1.assert_called_once()
    p2.assert_not_called()
    p3.assert_not_called()


# ===========================================================================
# TEST 2 - Primary 503 -> Backup succeeds
# ===========================================================================

def test_02_primary_503_backup_succeeds():
    """Primary=1 (503), Backup=1 (ok), OpenAI=0."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("503")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      return_value=_ok("Backup")) as p2, \
         patch.object(o.openai, "generate_advisory") as p3:

        advisory, meta = o.generate_advisory_with_fallback(*CALL_ARGS)

    assert advisory == _ok("Backup")
    assert meta["provider"] == "Google Gemini (Backup)"
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_not_called()


# ===========================================================================
# TEST 3 - Primary 429 -> Backup succeeds
# ===========================================================================

def test_03_primary_429_backup_succeeds():
    """Primary=1 (429), Backup=1 (ok), OpenAI=0."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("429")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      return_value=_ok("Backup")) as p2, \
         patch.object(o.openai, "generate_advisory") as p3:

        advisory, meta = o.generate_advisory_with_fallback(*CALL_ARGS)

    assert advisory == _ok("Backup")
    assert meta["provider"] == "Google Gemini (Backup)"
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_not_called()


# ===========================================================================
# TEST 4 - Primary 503 -> Backup 503 -> OpenAI succeeds
# ===========================================================================

def test_04_primary_503_backup_503_openai_succeeds():
    """Primary=1, Backup=1, OpenAI=1. Returns OpenAI advisory."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("503")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=TransientAIError("503")) as p2, \
         patch.object(o.openai, "generate_advisory",
                      return_value=_ok("OpenAI")) as p3:

        advisory, meta = o.generate_advisory_with_fallback(*CALL_ARGS)

    assert advisory == _ok("OpenAI")
    assert meta["provider"] == "OpenAI"
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_called_once()


# ===========================================================================
# TEST 5 - All providers fail -> AI_UNAVAILABLE
# ===========================================================================

def test_05_all_providers_fail_ai_unavailable():
    """Primary=1, Backup=1, OpenAI=1. Raises TransientAIError (AI_UNAVAILABLE)."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("503")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=TransientAIError("503")) as p2, \
         patch.object(o.openai, "generate_advisory",
                      side_effect=TransientAIError("429")) as p3:

        with pytest.raises(TransientAIError, match="All AI providers unavailable"):
            o.generate_advisory_with_fallback(*CALL_ARGS)

    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_called_once()


# ===========================================================================
# TEST 6 - Provider 503: underlying API called EXACTLY ONCE (no internal retry)
# ===========================================================================

def test_06_provider_503_no_internal_retry():
    """
    generate_content_with_retry must call client.models.generate_content
    exactly ONCE on 503. No retry loop, no sleep, no backoff.
    """
    from google.genai.errors import ServerError

    mock_client = MagicMock()
    err = MagicMock(spec=ServerError)
    err.code = 503
    mock_client.models.generate_content.side_effect = err

    with pytest.raises(Exception):
        generate_content_with_retry(
            client=mock_client,
            model="gemini-3.6-flash",
            contents="test",
            config=None,
        )

    assert mock_client.models.generate_content.call_count == 1, (
        "Provider retried internally on 503 - retry count MUST be zero"
    )


# ===========================================================================
# TEST 7 - Provider 429: underlying API called EXACTLY ONCE
# ===========================================================================

def test_07_provider_429_no_internal_retry():
    """generate_content_with_retry must call the API exactly once on 429."""
    from google.genai.errors import ClientError

    mock_client = MagicMock()
    err = MagicMock(spec=ClientError)
    err.code = 429
    mock_client.models.generate_content.side_effect = err

    with pytest.raises(Exception):
        generate_content_with_retry(
            client=mock_client,
            model="gemini-3.6-flash",
            contents="test",
            config=None,
        )

    assert mock_client.models.generate_content.call_count == 1, (
        "Provider retried internally on 429 - retry count MUST be zero"
    )


# ===========================================================================
# TEST 8 - Backup Gemini 503: underlying API called EXACTLY ONCE
# ===========================================================================

def test_08_backup_503_underlying_api_called_once():
    """Backup provider uses the same generate_content_with_retry - must be exactly once."""
    from google.genai.errors import ServerError

    mock_client = MagicMock()
    err = MagicMock(spec=ServerError)
    err.code = 503
    mock_client.models.generate_content.side_effect = err

    with pytest.raises(Exception):
        generate_content_with_retry(
            client=mock_client,
            model="gemini-3.6-flash",
            contents="test",
            config=None,
        )

    assert mock_client.models.generate_content.call_count == 1


# ===========================================================================
# TEST 9 - OpenAI transient failure: called EXACTLY ONCE, no retry
# ===========================================================================

def test_09_openai_transient_failure_called_exactly_once():
    """OpenAI is called exactly once on transient failure. No retry."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("503")), \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=TransientAIError("503")), \
         patch.object(o.openai, "generate_advisory",
                      side_effect=TransientAIError("transient")) as mock_oai:

        with pytest.raises(TransientAIError):
            o.generate_advisory_with_fallback(*CALL_ARGS)

    mock_oai.assert_called_once()


# ===========================================================================
# TEST 10 - Permanent primary error: no fallback, no retry
# ===========================================================================

def test_10_permanent_primary_error_no_fallback():
    """Permanent error -> PermanentAIError raised immediately; backup+OpenAI never called."""
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=PermanentAIError("400")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory") as p2, \
         patch.object(o.openai, "generate_advisory") as p3:

        with pytest.raises(PermanentAIError):
            o.generate_advisory_with_fallback(*CALL_ARGS)

    p1.assert_called_once()
    p2.assert_not_called()
    p3.assert_not_called()


# ===========================================================================
# Regression suite (pre-existing scenarios, explicit per-provider counts)
# ===========================================================================

def test_reg_primary_succeeds_no_fallback():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory", return_value={"advice": "Primary"}) as p1, \
         patch.object(o.gemini_backup, "generate_advisory") as p2, \
         patch.object(o.openai, "generate_advisory") as p3:
        advisory, meta = o.generate_advisory_with_fallback("prompt", "sys", {})
    assert advisory == {"advice": "Primary"}
    assert meta["provider"] == "Google Gemini"
    p1.assert_called_once()
    p2.assert_not_called()
    p3.assert_not_called()


def test_reg_primary_429_backup_succeeds():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("429")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      return_value={"advice": "Backup"}) as p2, \
         patch.object(o.openai, "generate_advisory") as p3:
        advisory, meta = o.generate_advisory_with_fallback("prompt", "sys", {})
    assert advisory == {"advice": "Backup"}
    assert meta["provider"] == "Google Gemini (Backup)"
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_not_called()


def test_reg_primary_429_backup_fails_openai_called():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("Quota")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=TransientAIError("Backup Quota")) as p2, \
         patch.object(o.openai, "generate_advisory",
                      return_value={"advice": "OpenAI"}) as p3:
        advisory, meta = o.generate_advisory_with_fallback("prompt", "sys", {})
    assert advisory == {"advice": "OpenAI"}
    assert meta["provider"] == "OpenAI"
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_called_once()


def test_reg_primary_permanent_error():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=PermanentAIError("Invalid")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory") as p2, \
         patch.object(o.openai, "generate_advisory") as p3:
        with pytest.raises(PermanentAIError):
            o.generate_advisory_with_fallback("prompt", "sys", {})
    p1.assert_called_once()
    p2.assert_not_called()
    p3.assert_not_called()


def test_reg_backup_key_missing():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("Quota")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=AIConfigurationError("Key missing")) as p2, \
         patch.object(o.openai, "generate_advisory",
                      return_value={"advice": "OpenAI"}) as p3:
        advisory, meta = o.generate_advisory_with_fallback("prompt", "sys", {})
    assert advisory == {"advice": "OpenAI"}
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_called_once()


def test_reg_all_fail():
    o = _orch()
    with patch.object(o.gemini, "generate_advisory",
                      side_effect=TransientAIError("Error")) as p1, \
         patch.object(o.gemini_backup, "generate_advisory",
                      side_effect=TransientAIError("Error")) as p2, \
         patch.object(o.openai, "generate_advisory",
                      side_effect=TransientAIError("Error")) as p3:
        with pytest.raises(TransientAIError, match="All AI providers unavailable"):
            o.generate_advisory_with_fallback("prompt", "sys", {})
    p1.assert_called_once()
    p2.assert_called_once()
    p3.assert_called_once()
