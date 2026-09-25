import time
import random
import logging
from google.genai.errors import ServerError

logger = logging.getLogger(__name__)

def generate_content_with_retry(client, model, contents, config=None, max_attempts=3):
    """
    Calls Gemini generate_content with bounded exponential backoff.
    Retries ONLY on google.genai.errors.ServerError with code 503.
    """
    attempt = 1
    while True:
        try:
            return client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except ServerError as e:
            if hasattr(e, 'code') and e.code == 503:
                if attempt < max_attempts:
                    logger.warning(f"Gemini 503 detected (attempt {attempt}/{max_attempts}). Retrying...")
                    # Exponential backoff: ~1s, ~2s
                    base_wait = 2 ** (attempt - 1)
                    jitter = random.uniform(0.1, 0.5)
                    time.sleep(base_wait + jitter)
                    attempt += 1
                    continue
                else:
                    logger.warning(f"Gemini 503 detected (attempt {attempt}/{max_attempts}). Not retrying, max attempts exhausted.")

            # Non-503 ServerError or exhausted attempts
            raise e
