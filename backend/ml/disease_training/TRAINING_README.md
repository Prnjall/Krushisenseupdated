# KrushiSense Disease Model - Colab Training Guide

This directory contains the necessary script to train the KrushiSense Disease MobileNetV3-Small classifier offline using Google Colab's GPU. 

Because the Django production backend does not have GPUs or deep learning frameworks, **do not attempt to run this script on the production server.**

## 1. How to open the script in Google Colab
1. Go to [Google Colab](https://colab.research.google.com/).
2. Create a **New Notebook**.
3. Create a single cell and copy-paste the entire contents of `train_disease_model_colab.py` into it.

## 2. How to enable GPU
1. In the Colab menu bar, click **Runtime** > **Change runtime type**.
2. Under "Hardware accelerator", select **T4 GPU** (or any available GPU).
3. Click **Save**.

## 3. Where to place the datasets
1. In the Colab sidebar, click the **Folder icon** (Files).
2. Create a folder named `dataset` right inside `/content/` (so the path is `/content/dataset`).
3. Upload the unzipped PlantVillage, PlantDoc, and Rice datasets into this folder. 
4. The folder structure should look like:
   ```
   /content/dataset/
       Apple___Apple_scab/
       Apple___Black_rot/
       Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot/
       ...
   ```
*(The script automatically uses `class_mapping.json` logic to map these source folder names to the correct canonical KrushiSense classes).*

## 4. How to run each stage
1. Before running the script cell, create a new code cell at the top and run the following command to install required dependencies:
   ```bash
   !pip install torch torchvision onnx onnxruntime scikit-learn matplotlib pandas Pillow
   ```
2. Run the main script cell.
3. The script will automatically:
   - Scan, hash, and de-duplicate images.
   - Print an inventory of found images and rejected classes.
   - Train the MobileNetV3 model for up to 15 epochs with early stopping.
   - Evaluate the model on the 10% hold-out test set.
   - Export the ONNX artifact.

## 5. What files will be produced
The script will create an `/content/output` folder containing:
- `disease_classifier.onnx` (The final model)
- `class_names.json` (Index to class name mapping)
- `preprocessing.json` (Normalization metadata)
- `model_metadata.json` (Accuracies and threshold)
- `training_metrics.json` (Epoch loss/acc records)
- `confusion_matrix.png` (Visual matrix of test set performance)
- `training_curves.png` (Visual plots of loss/acc over epochs)
- `per_class_metrics.csv` (F1 score for each individual disease class)
- `dataset_inventory.csv` (SHA-256 hashes of every training image)

## 6. How to verify that the ONNX model is valid
The script automatically runs ONNX verification at the end of the export phase via `onnx.checker.check_model(onnx_model)`. If you see `ONNX model verification SUCCESS` in the Colab output logs, the model structure is valid.

## 7. Metrics to review before integrating into Django
Before downloading these files and moving them into Django, you **must review**:
1. **Per-Class Metrics (`per_class_metrics.csv`)**: Ensure no single class has a drastically low F1 score (e.g., < 0.60). If it does, the model is failing on that specific disease.
2. **Confusion Matrix (`confusion_matrix.png`)**: Check if the model is heavily confusing one crop with another (e.g., Apple Scab vs Maize Blight). 
3. **Validation Threshold**: Review the confidence threshold generated in `model_metadata.json`.

If the model is satisfactory, download the `.onnx` and `.json` files and place them in the Django `backend/predictions/models/disease_model/` directory.

---
**MODEL_READY_FOR_DJANGO_INTEGRATION = NO** *(Pending actual Colab execution)*
