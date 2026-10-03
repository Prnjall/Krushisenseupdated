import logging
from google.genai.errors import ServerError

logger = logging.getLogger(__name__)

def generate_content_with_retry(client, model, contents, config=None, max_attempts=1):
    """
    Calls Gemini generate_content with no provider-level retry.

    max_attempts is kept for API compatibility but defaults to 1 (single attempt).
    Provider-level retries have been removed: the orchestrator is solely responsible
    for fallback across providers. Retrying the same provider wastes quota and delays
    the user when a faster fallback provider is available.

    Any ServerError (503, 500, etc.) or ClientError is raised immediately so the
    orchestrator can decide whether to call the backup provider.
    """
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
