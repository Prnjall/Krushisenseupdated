import io
import logging
from PIL import Image
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

# Enforce the existing disease-image upload limit of 5 MB.
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 1024
JPEG_QUALITY = 85

class ImageValidationError(Exception):
    """Controlled exception for any image validation or processing failure."""
    pass

def preprocess_multimodal_image(image_bytes: bytes, mime_type: str = "") -> Tuple[bytes, str, Dict[str, Any]]:
    """
    Validates, sanitizes, and resizes an uploaded image for multimodal AI usage.
    Strips EXIF data and forces output to image/jpeg.
    All processing is performed in-memory.

    Args:
        image_bytes (bytes): The raw uploaded image payload.
        mime_type (str): Original MIME type from the client (optional, untrusted).

    Returns:
        Tuple containing:
          - sanitized_bytes (bytes): The clean JPEG image bytes.
          - sanitized_mime_type (str): Always "image/jpeg".
          - metadata (dict): Safe metadata (e.g., new dimensions).

    Raises:
        ImageValidationError: If the image is oversized, corrupted, or cannot be processed.
    """
    original_size = len(image_bytes)

    if original_size > MAX_IMAGE_SIZE_BYTES:
        logger.warning(f"Image preprocessing failed: Payload size ({original_size} bytes) exceeds limit.")
        raise ImageValidationError("Image size exceeds the maximum limit of 5MB.")

    try:
        # Load the image from bytes
        # Image.open is lazy, but verify checks the integrity of the header
        with Image.open(io.BytesIO(image_bytes)) as img:
            img.verify()
    except Image.DecompressionBombError:
        logger.warning("Image preprocessing failed: Decompression bomb detected.")
        raise ImageValidationError("Image dimensions are unreasonably large.")
    except Exception as e:
        logger.warning("Image preprocessing failed during verification.")
        raise ImageValidationError("Invalid or corrupted image format.")

    try:
        # Re-open the image because verify() modifies the internal state
        with Image.open(io.BytesIO(image_bytes)) as img:
            # 1. Strip EXIF securely
            # Convert to RGB (also handles alpha channels if PNG)
            rgb_img = img.convert("RGB")
            
            # Create a completely fresh image without any original info dict
            clean_img = Image.new("RGB", rgb_img.size)
            clean_img.paste(rgb_img, (0, 0))
            
            # 2. Resize maintaining aspect ratio
            clean_img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

            final_width, final_height = clean_img.size

            # 3. Save as fresh JPEG to a new buffer
            output_buffer = io.BytesIO()
            clean_img.save(output_buffer, format="JPEG", quality=JPEG_QUALITY)
            
            sanitized_bytes = output_buffer.getvalue()

            metadata = {
                "original_size_bytes": original_size,
                "sanitized_size_bytes": len(sanitized_bytes),
                "width": final_width,
                "height": final_height
            }
            
            # Log safe metadata, NEVER log the raw bytes or EXIF
            logger.info(f"Image successfully preprocessed for vision advisory: {final_width}x{final_height}, size {len(sanitized_bytes)} bytes.")

            return sanitized_bytes, "image/jpeg", metadata

    except Exception as e:
        logger.warning("Image preprocessing failed during processing.")
        raise ImageValidationError("Unable to process the uploaded image.")
