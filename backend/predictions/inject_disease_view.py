import sys

with open(r"P:\Agri Analysis\backend\predictions\views.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

import_idx = 0
for i, line in enumerate(lines):
    if line.startswith("import json"):
        import_idx = i
        break

lines.insert(import_idx + 1, "import io\nfrom PIL import Image\nimport onnxruntime as ort\n")

# Find the insertion point before "__main__"
main_idx = len(lines)
for i, line in enumerate(lines):
    if line.startswith('if __name__ == "__main__":'):
        main_idx = i
        break

# Disease Model Initialization
disease_init = """
# ==============================
# Load Disease Model
# ==============================
DISEASE_MODELS_DIR = MODELS_DIR / "disease_model"
disease_onnx_path = DISEASE_MODELS_DIR / "disease_classifier.onnx"
class_names_path = DISEASE_MODELS_DIR / "class_names.json"
preprocessing_path = DISEASE_MODELS_DIR / "preprocessing.json"
metadata_path = DISEASE_MODELS_DIR / "model_metadata.json"

disease_session = None
disease_class_names = []
disease_preprocessing = {}
disease_confidence_threshold = 0.60

try:
    if disease_onnx_path.exists():
        disease_session = ort.InferenceSession(str(disease_onnx_path), providers=['CPUExecutionProvider'])
        
    if class_names_path.exists():
        with open(class_names_path, "r") as f:
            disease_class_names = json.load(f)
            
    if preprocessing_path.exists():
        with open(preprocessing_path, "r") as f:
            disease_preprocessing = json.load(f)
            
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            md = json.load(f)
            disease_confidence_threshold = md.get("confidence_threshold", 0.60)
            
    logger.info("Disease model artifacts loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load disease model artifacts: {e}")

DISEASE_CROP_MAPPING = {
    'apple': ['apple_healthy', 'apple_scab', 'apple_black_rot'],
    'maize': ['maize_healthy', 'maize_cercospora_leaf_spot', 'maize_common_rust', 'maize_northern_leaf_blight'],
    'grapes': ['grape_healthy', 'grape_black_rot', 'grape_esca', 'grape_leaf_blight'],
    'rice': ['rice_healthy', 'rice_bacterial_leaf_blight', 'rice_brown_spot', 'rice_leaf_smut']
}

def format_disease_name(class_name):
    if class_name.endswith("_healthy"):
        return "Healthy"
    # e.g., apple_black_rot -> Apple Black Rot
    parts = class_name.split("_")
    return " ".join([p.capitalize() for p in parts])

# ==============================
# Disease Detection API
# ==============================
@csrf_exempt
@require_POST
def disease_detection_view(request):
    try:
        # 1. Model Availability Check
        if not disease_session or not disease_class_names or not disease_preprocessing:
            return JsonResponse({
                "success": False,
                "status": "ANALYSIS_UNAVAILABLE",
                "message": "Disease detection model is currently unavailable."
            })
            
        # 2. Crop Validation
        crop = request.POST.get("crop", "").lower().strip()
        if crop not in DISEASE_CROP_MAPPING:
            return JsonResponse({
                "success": False,
                "status": "UNSUPPORTED_CROP",
                "message": "Disease detection is currently unavailable for this crop."
            })
            
        # 3. Image Validation
        if "image" not in request.FILES:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "No image provided."
            })
            
        image_file = request.FILES["image"]
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "Image size exceeds 5MB."
            })
            
        try:
            image_data = image_file.read()
            img = Image.open(io.BytesIO(image_data))
            img.verify() # Verify it's an actual image
            
            # Re-open for processing because verify() breaks the file pointer
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "Invalid or corrupted image format."
            })
            
        # 4. Preprocessing
        # Uses ImageNet stats by default as per preprocessing.json
        img = img.resize((224, 224), Image.BILINEAR)
        img_np = np.array(img).astype(np.float32) / 255.0
        
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_np = (img_np - mean) / std
        
        # HWC to CHW
        img_np = np.transpose(img_np, (2, 0, 1))
        # Add batch dimension
        img_np = np.expand_dims(img_np, axis=0)
        
        # 5. Inference
        input_name = disease_session.get_inputs()[0].name
        logits = disease_session.run(None, {input_name: img_np})[0]
        
        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        probs = probs[0]
        
        pred_idx = int(np.argmax(probs))
        pred_class = disease_class_names[pred_idx]
        confidence = float(probs[pred_idx])
        
        # 6. Post-Processing & Safety Validation
        allowed_classes = DISEASE_CROP_MAPPING[crop]
        
        if pred_class not in allowed_classes or confidence < disease_confidence_threshold:
            return JsonResponse({
                "success": True,
                "status": "LOW_CONFIDENCE",
                "crop": crop,
                "diagnosis": None,
                "confidence": round(confidence, 4)
            })
            
        if pred_class.endswith("_healthy"):
            status = "HEALTHY"
        else:
            status = "DISEASE_DETECTED"
            
        return JsonResponse({
            "success": True,
            "status": status,
            "crop": crop,
            "diagnosis": {
                "disease": format_disease_name(pred_class),
                "class_name": pred_class,
                "confidence": round(confidence, 4)
            }
        })
        
    except Exception as e:
        logger.error(f"Disease detection error: {e}")
        # Never expose internal Python stack traces
        return JsonResponse({
            "success": False,
            "status": "ANALYSIS_UNAVAILABLE",
            "message": "An error occurred during analysis."
        })

"""

lines.insert(main_idx, disease_init)

with open(r"P:\Agri Analysis\backend\predictions\views.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Updated views.py successfully.")
