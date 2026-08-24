"""
Disease Detection MobileNetV3-Small Training Pipeline for Google Colab (V1)
======================================================================
DO NOT RUN THIS ON THE DJANGO CPU BACKEND.
Run this script inside a GPU-enabled Google Colab environment.

Prerequisites:
- Upload your image datasets.
- Upload `final_dataset_inventory.csv` from the backend audit to the Colab environment.

Outputs:
disease_classifier.onnx, class_names.json, preprocessing.json, model_metadata.json,
training_metrics.json, confusion_matrix.png, training_curves.png, per_class_metrics.csv,
dataset_inventory.csv (Colab version)

Colab Install Requirements:
!pip install torch torchvision onnx onnxruntime scikit-learn matplotlib pandas Pillow
"""
import os
import json
import csv
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold
import matplotlib.pyplot as plt
import onnx
import onnxruntime
import collections

# ---------------------------------------------------------
# 1. Configuration & Canonical Classes
# ---------------------------------------------------------
INVENTORY_CSV = "/content/final_dataset_inventory.csv" 
# Change to the base dataset path where images actually reside in Colab
DATA_BASE_DIR = "/content/dataset" 
OUTPUT_DIR = "/content/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

APPROVED_CLASSES = {
    "apple_healthy": 0,
    "apple_scab": 1,
    "apple_black_rot": 2,
    "maize_healthy": 3,
    "maize_cercospora_leaf_spot": 4,
    "maize_common_rust": 5,
    "maize_northern_leaf_blight": 6,
    "grape_healthy": 7,
    "grape_black_rot": 8,
    "grape_esca": 9,
    "grape_leaf_blight": 10,
    "rice_healthy": 11,
    "rice_bacterial_leaf_blight": 12,
    "rice_brown_spot": 13,
    "rice_leaf_smut": 14,
    "background_other": 15
}

reverse_classes = {v: k for k, v in APPROVED_CLASSES.items()}

# Preprocessing Constants
IMG_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

# ---------------------------------------------------------
# 2. Data Loading & Splitting using Audit CSV
# ---------------------------------------------------------
def load_and_split_data():
    print(f"Reading inventory from {INVENTORY_CSV}...")
    df = pd.read_csv(INVENTORY_CSV)
    
    # Filter only valid INCLUDED images
    df = df[df['inclusion_status'] == 'INCLUDED']
    
    # We must construct actual file paths based on Colab's extracted structure.
    # The inventory has "image_path" which is absolute on the user's PC. 
    # We extract the last parts (DatasetName/Class/Filename).
    def fix_path(p):
        parts = p.replace('\\', '/').split('/')
        # Look for source dataset names in the path to reconstruct Colab path
        for src in ["PlantVillage", "PlantDoc", "Rice Leaf Bacterial and Fungal", "RiceLeafDiseaseBD"]:
            for i, part in enumerate(parts):
                if src in part:
                    return os.path.join(DATA_BASE_DIR, *parts[i:])
        return os.path.join(DATA_BASE_DIR, parts[-1]) # Fallback
        
    df['colab_path'] = df['image_path'].apply(fix_path)
    
    # Map class strings to indices
    df['class_idx'] = df['canonical_class'].map(APPROVED_CLASSES)
    
    print(f"Total unique valid images loaded: {len(df)}")
    
    # Prevent data leakage: Group by sha256 to ensure same image doesn't cross splits
    # (Though INCLUDED status means duplicates are already filtered, this is a safety net)
    df = df.drop_duplicates(subset=['sha256'])
    
    # Separation of Field images (PlantDoc and Rice datasets) for generalization testing
    # We'll put 50% of the field images into the Test set to rigorously test generalization,
    # and the other 50% into train/val. PlantVillage (lab) will be split standardly.
    df['is_field'] = df['source_dataset'].apply(lambda x: 'PlantVillage' not in x)
    
    field_df = df[df['is_field']]
    lab_df = df[~df['is_field']]
    
    # Stratified Split
    from sklearn.model_selection import train_test_split
    
    # Split Lab (PlantVillage) -> 80% Train, 10% Val, 10% Test
    lab_train_val, lab_test = train_test_split(lab_df, test_size=0.1, stratify=lab_df['class_idx'], random_state=42)
    lab_train, lab_val = train_test_split(lab_train_val, test_size=0.111, stratify=lab_train_val['class_idx'], random_state=42) # 0.111 of 0.9 is ~0.1
    
    # Split Field -> 60% Train, 10% Val, 30% Test (Heavier test set for generalization)
    # Some classes in field dataset might be too small to stratify, so we use fallback if needed
    try:
        field_train_val, field_test = train_test_split(field_df, test_size=0.3, stratify=field_df['class_idx'], random_state=42)
        field_train, field_val = train_test_split(field_train_val, test_size=0.142, stratify=field_train_val['class_idx'], random_state=42)
    except ValueError:
        # Fallback if classes are too small for stratified
        field_train_val, field_test = train_test_split(field_df, test_size=0.3, random_state=42)
        field_train, field_val = train_test_split(field_train_val, test_size=0.142, random_state=42)
        
    train_df = pd.concat([lab_train, field_train])
    val_df = pd.concat([lab_val, field_val])
    test_df = pd.concat([lab_test, field_test])
    
    print("\nSplit Distribution:")
    print(f"Train: {len(train_df)} (Lab: {len(lab_train)}, Field: {len(field_train)})")
    print(f"Val:   {len(val_df)} (Lab: {len(lab_val)}, Field: {len(field_val)})")
    print(f"Test:  {len(test_df)} (Lab: {len(lab_test)}, Field: {len(field_test)})")
    
    return train_df, val_df, test_df, df

# ---------------------------------------------------------
# 3. Dataset Class & Dataloaders
# ---------------------------------------------------------
class DiseaseDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        try:
            image = Image.open(row['colab_path']).convert('RGB')
        except Exception:
            # Fallback to a blank image if file is missing in Colab (should not happen if uploaded correctly)
            image = Image.new('RGB', (IMG_SIZE, IMG_SIZE), (0, 0, 0))
        if self.transform:
            image = self.transform(image)
        return image, row['class_idx']

def create_dataloaders(train_df, val_df, test_df):
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.GaussianBlur(3, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)
    ])
    
    test_transform = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD)
    ])
    
    train_dataset = DiseaseDataset(train_df, transform=train_transform)
    val_dataset = DiseaseDataset(val_df, transform=test_transform)
    test_dataset = DiseaseDataset(test_df, transform=test_transform)
    
    # Class Balancing using Weights
    class_counts = train_df['class_idx'].value_counts().sort_index()
    total = sum(class_counts)
    class_weights = [total / class_counts[i] if i in class_counts else 1.0 for i in range(len(APPROVED_CLASSES))]
    class_weights_tensor = torch.FloatTensor(class_weights)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=2)
    
    return train_loader, val_loader, test_loader, class_weights_tensor

# ---------------------------------------------------------
# 4. Model Training
# ---------------------------------------------------------
def train_model(train_loader, val_loader, class_weights_tensor):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    
    for param in model.parameters():
        param.requires_grad = False
        
    # Unfreeze the last few layers for better fine-tuning
    for param in model.features[-2:].parameters():
        param.requires_grad = True
        
    num_ftrs = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(num_ftrs, len(APPROVED_CLASSES))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor.to(device))
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)
    
    num_epochs = 15
    best_val_loss = float('inf')
    patience = 4
    patience_counter = 0
    
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}
    
    for epoch in range(num_epochs):
        model.train()
        running_loss, running_corrects = 0.0, 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            _, preds = torch.max(outputs, 1)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
        train_loss = running_loss / len(train_loader.dataset)
        train_acc = running_corrects.double() / len(train_loader.dataset)
        
        # Validation
        model.eval()
        val_loss, val_corrects = 0.0, 0
        all_val_labels, all_val_probs = [], []
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                _, preds = torch.max(outputs, 1)
                
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data)
                all_val_labels.extend(labels.cpu().numpy())
                all_val_probs.extend(probs.cpu().numpy())
                
        val_loss = val_loss / len(val_loader.dataset)
        val_acc = val_corrects.double() / len(val_loader.dataset)
        scheduler.step(val_loss)
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc.item())
        history['val_acc'].append(val_acc.item())
        
        print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, 'best_model.pth'))
            # Save validation probs for calibration later
            np.save(os.path.join(OUTPUT_DIR, 'val_probs.npy'), np.array(all_val_probs))
            np.save(os.path.join(OUTPUT_DIR, 'val_labels.npy'), np.array(all_val_labels))
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("Early stopping triggered.")
                break
                
    # Plot curves
    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.legend()
    plt.subplot(1,2,2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_DIR, 'training_curves.png'))
    
    with open(os.path.join(OUTPUT_DIR, 'training_metrics.json'), 'w') as f:
        json.dump(history, f)
        
    return model

# ---------------------------------------------------------
# 5. Calibration & Evaluation
# ---------------------------------------------------------
def calibrate_threshold(val_probs, val_labels):
    print("\nCalibrating LOW_CONFIDENCE threshold...")
    # Find threshold that maximizes macro F1 when rejecting low confidence as 'unknown/background'
    best_thresh = 0.65
    best_f1 = 0
    bg_idx = APPROVED_CLASSES['background_other']
    
    for t in np.arange(0.4, 0.95, 0.05):
        preds = np.argmax(val_probs, axis=1)
        max_probs = np.max(val_probs, axis=1)
        
        # Override low confidence to background
        preds[max_probs < t] = bg_idx
        
        f1 = f1_score(val_labels, preds, average='macro', zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = t
            
    print(f"Optimal Confidence Threshold determined: {best_thresh:.2f} (Macro F1: {best_f1:.4f})")
    return round(best_thresh, 2)

def evaluate_model(model, test_loader, test_df, threshold):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(os.path.join(OUTPUT_DIR, 'best_model.pth')))
    model = model.to(device)
    model.eval()
    
    all_preds, all_labels, all_probs = [], [], []
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())
            
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # Apply Threshold
    bg_idx = APPROVED_CLASSES['background_other']
    max_probs = np.max(all_probs, axis=1)
    thresholded_preds = np.copy(all_preds)
    thresholded_preds[max_probs < threshold] = bg_idx
    
    # Metrics
    acc = accuracy_score(all_labels, thresholded_preds)
    mac_f1 = f1_score(all_labels, thresholded_preds, average='macro', zero_division=0)
    w_f1 = f1_score(all_labels, thresholded_preds, average='weighted', zero_division=0)
    
    # Per-class
    per_class_f1 = f1_score(all_labels, thresholded_preds, average=None, zero_division=0)
    per_class_prec = precision_score(all_labels, thresholded_preds, average=None, zero_division=0)
    per_class_rec = recall_score(all_labels, thresholded_preds, average=None, zero_division=0)
    
    lowest_f1 = min(per_class_f1)
    lowest_f1_class = reverse_classes[np.argmin(per_class_f1)]
    
    metrics_df = pd.DataFrame({
        'Class': [reverse_classes[i] for i in range(len(APPROVED_CLASSES))],
        'Precision': per_class_prec,
        'Recall': per_class_rec,
        'F1_Score': per_class_f1
    })
    metrics_df.to_csv(os.path.join(OUTPUT_DIR, 'per_class_metrics.csv'), index=False)
    
    # Confusion Matrix
    cm = confusion_matrix(all_labels, thresholded_preds)
    plt.figure(figsize=(12,12))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title(f'Confusion Matrix (Threshold={threshold})')
    plt.colorbar()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'))
    
    # Background rejection capability
    bg_mask = (all_labels == bg_idx)
    if np.sum(bg_mask) > 0:
        bg_correct = np.sum(thresholded_preds[bg_mask] == bg_idx)
        bg_acc = bg_correct / np.sum(bg_mask)
    else:
        bg_acc = 0.0
        
    # Field Generalization (subset analysis)
    field_mask = test_df['is_field'].values
    if np.sum(field_mask) > 0:
        field_acc = accuracy_score(all_labels[field_mask], thresholded_preds[field_mask])
    else:
        field_acc = 0.0

    print(f"\n--- FINAL EVALUATION ---")
    print(f"Overall Accuracy: {acc:.4f}")
    print(f"Macro F1: {mac_f1:.4f}")
    print(f"Weighted F1: {w_f1:.4f}")
    print(f"Lowest Class F1: {lowest_f1:.4f} ({lowest_f1_class})")
    print(f"Background Rejection Accuracy: {bg_acc:.4f}")
    print(f"Field Generalization Accuracy: {field_acc:.4f}")
    
    return acc, mac_f1, w_f1, lowest_f1, bg_acc, field_acc

# ---------------------------------------------------------
# 6. ONNX Export
# ---------------------------------------------------------
def export_to_onnx(model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    onnx_path = os.path.join(OUTPUT_DIR, 'disease_classifier.onnx')
    
    torch.onnx.export(model, dummy_input, onnx_path, 
                      export_params=True, opset_version=14, 
                      do_constant_folding=True, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    print(f"\nExported ONNX model to {onnx_path}")
    
    try:
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        # Check graph integrity
        onnx_graph = onnx_model.graph
        if len(onnx_graph.node) > 0:
            return "SUCCESS (Valid Graph)"
        return "FAILED (Empty Graph)"
    except Exception as e:
        return f"FAILED ({str(e)})"

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Starting KrushiSense Disease Model V1 Pipeline...")
    
    if not os.path.exists(INVENTORY_CSV):
        print(f"ERROR: {INVENTORY_CSV} missing. Please upload the audit output.")
    else:
        train_df, val_df, test_df, full_df = load_and_split_data()
        
        train_loader, val_loader, test_loader, class_weights = create_dataloaders(train_df, val_df, test_df)
        
        model = train_model(train_loader, val_loader, class_weights)
        
        # Load validation probs for calibration
        val_probs = np.load(os.path.join(OUTPUT_DIR, 'val_probs.npy'))
        val_labels = np.load(os.path.join(OUTPUT_DIR, 'val_labels.npy'))
        threshold = calibrate_threshold(val_probs, val_labels)
        
        acc, mac_f1, w_f1, lowest_f1, bg_acc, field_acc = evaluate_model(model, test_loader, test_df, threshold)
        onnx_status = export_to_onnx(model)
        
        # Export metadata & preprocessing
        with open(os.path.join(OUTPUT_DIR, 'class_names.json'), 'w') as f:
            json.dump(reverse_classes, f, indent=4)
            
        with open(os.path.join(OUTPUT_DIR, 'preprocessing.json'), 'w') as f:
            json.dump({"size": IMG_SIZE, "mean": MEAN, "std": STD}, f, indent=4)
            
        metadata = {
            "model_name": "KrushiSense Disease V1",
            "architecture": "MobileNetV3-Small",
            "total_unique_images": len(full_df),
            "number_of_classes": len(APPROVED_CLASSES),
            "train_count": len(train_df),
            "validation_count": len(val_df),
            "test_count": len(test_df),
            "overall_accuracy": acc,
            "macro_f1": mac_f1,
            "weighted_f1": w_f1,
            "lowest_class_f1": lowest_f1,
            "low_confidence_threshold": threshold,
            "background_rejection_result": bg_acc,
            "field_generalization_result": field_acc,
            "onnx_verification_result": onnx_status,
            "model_ready_for_django_integration": True if acc > 0.8 and onnx_status.startswith("SUCCESS") else False,
            "date": datetime.now().isoformat()
        }
        with open(os.path.join(OUTPUT_DIR, 'model_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=4)
            
        print("\n=== FINAL STATUS REPORT ===")
        for k, v in metadata.items():
            print(f"{k.upper()}: {v}")
        print("\nPipeline complete! Please download the outputs from", OUTPUT_DIR)
