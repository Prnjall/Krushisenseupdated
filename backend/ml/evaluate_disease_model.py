import os
import sys

def main():
    model_path = 'P:\\Agri Analysis\\backend\\ml\\disease_training\\output\\disease_classifier.onnx'
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found at {model_path}")
        
        report = """=================================================
DISEASE MODEL FINAL EVALUATION REPORT
=================================================

MODEL_NAME: KrushiSense Disease V1
TOTAL_UNIQUE_IMAGES: 16404
NUMBER_OF_CLASSES: 16
TRAIN_COUNT: N/A
VALIDATION_COUNT: N/A
TEST_COUNT: N/A

OVERALL_ACCURACY: N/A
MACRO_PRECISION: N/A
MACRO_RECALL: N/A
MACRO_F1: N/A
WEIGHTED_PRECISION: N/A
WEIGHTED_RECALL: N/A
WEIGHTED_F1: N/A

LOWEST_CLASS_F1: N/A
LOWEST_PERFORMING_CLASS: N/A

LOW_CONFIDENCE_THRESHOLD: N/A

BACKGROUND_PRECISION: N/A
BACKGROUND_RECALL: N/A
BACKGROUND_F1: N/A
BACKGROUND_FALSE_POSITIVE_RATE: N/A

FIELD_GENERALIZATION_RESULT: NOT_AVAILABLE

ONNX_VERIFICATION_RESULT: FAILED (Model file not found)
ONNX_PYTORCH_PREDICTION_MATCH: FAIL

FINAL_MODEL_SAFETY_ASSESSMENT:
The evaluation could not be completed because the trained ONNX model files are missing from the workspace. No physical evaluation could be performed against the hold-out test data.

MODEL_READY_FOR_DJANGO_INTEGRATION = NO
"""
        with open('P:\\Agri Analysis\\backend\\ml\\disease_model_final_evaluation_report.txt', 'w') as f:
            f.write(report)
        sys.exit(1)

if __name__ == '__main__':
    main()
