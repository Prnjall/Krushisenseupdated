import io
import unittest
from PIL import Image
from predictions.image_utils import preprocess_multimodal_image, ImageValidationError, MAX_IMAGE_SIZE_BYTES

class TestImageUtils(unittest.TestCase):
    def create_test_image(self, width, height, format="JPEG", **kwargs):
        img = Image.new("RGB", (width, height), color="red")
        buffer = io.BytesIO()
        img.save(buffer, format=format, **kwargs)
        return buffer.getvalue()

    def test_valid_image(self):
        img_bytes = self.create_test_image(800, 600, format="JPEG")
        sanitized_bytes, mime_type, metadata = preprocess_multimodal_image(img_bytes, "image/jpeg")
        
        self.assertEqual(mime_type, "image/jpeg")
        self.assertEqual(metadata["width"], 800)
        self.assertEqual(metadata["height"], 600)
        
        # Verify it's a valid JPEG
        with Image.open(io.BytesIO(sanitized_bytes)) as out_img:
            self.assertEqual(out_img.format, "JPEG")
            self.assertEqual(out_img.size, (800, 600))

    def test_resize(self):
        img_bytes = self.create_test_image(2000, 1000, format="PNG")
        sanitized_bytes, mime_type, metadata = preprocess_multimodal_image(img_bytes)
        
        self.assertEqual(metadata["width"], 1024)
        self.assertEqual(metadata["height"], 512)
        
        with Image.open(io.BytesIO(sanitized_bytes)) as out_img:
            self.assertEqual(out_img.size, (1024, 512))

    def test_existing_small_image(self):
        img_bytes = self.create_test_image(500, 500, format="JPEG")
        sanitized_bytes, mime_type, metadata = preprocess_multimodal_image(img_bytes)
        
        self.assertEqual(metadata["width"], 500)
        self.assertEqual(metadata["height"], 500)

    def test_exif_stripping(self):
        img = Image.new("RGB", (800, 600), color="blue")
        exif = img.getexif()
        # Set some dummy EXIF, e.g., Software or GPSInfo if possible
        exif[305] = "TestSoftware" # Software tag
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", exif=exif)
        img_bytes = buffer.getvalue()
        
        # Ensure it has EXIF initially
        with Image.open(io.BytesIO(img_bytes)) as test_img:
            self.assertIsNotNone(test_img.getexif())
            self.assertTrue(305 in test_img.getexif())

        sanitized_bytes, mime_type, metadata = preprocess_multimodal_image(img_bytes)
        
        # Ensure it has NO EXIF in output
        with Image.open(io.BytesIO(sanitized_bytes)) as out_img:
            out_exif = out_img.getexif()
            self.assertFalse(305 in out_exif)

    def test_invalid_image(self):
        bad_bytes = b"This is just some text, not an image"
        with self.assertRaises(ImageValidationError) as context:
            preprocess_multimodal_image(bad_bytes)
        self.assertIn("Invalid or corrupted image format", str(context.exception))

    def test_corrupted_image(self):
        img_bytes = self.create_test_image(800, 600, format="JPEG")
        corrupted_bytes = img_bytes[:100] # Truncated
        with self.assertRaises(ImageValidationError):
            preprocess_multimodal_image(corrupted_bytes)

    def test_oversized_upload(self):
        # Create a payload > 5MB
        oversize_bytes = b"0" * (MAX_IMAGE_SIZE_BYTES + 1)
        with self.assertRaises(ImageValidationError) as context:
            preprocess_multimodal_image(oversize_bytes)
        self.assertIn("exceeds the maximum limit", str(context.exception))
        
    def test_output_size(self):
        # A large image (within 5MB but visually large enough to reduce size via compression)
        img_bytes = self.create_test_image(3000, 3000, format="JPEG")
        sanitized_bytes, mime_type, metadata = preprocess_multimodal_image(img_bytes)
        
        # Ensure the resized image is smaller in bytes
        self.assertLess(metadata["sanitized_size_bytes"], metadata["original_size_bytes"])
