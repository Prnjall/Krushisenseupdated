"""
KrushiSense Disease V1 Full Local Training & Evaluation Pipeline
======================================================================
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
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import onnx
import onnxruntime

# ---------------------------------------------------------
# 1. Configuration & 15 Populated Classes
# ---------------------------------------------------------
INVENTORY_CSV = r"P:\Agri Analysis\backend\ml\disease_dataset\final_dataset_inventory.csv"
DATA_BASE_DIR = r"P:\Agri Analysis\backend\ml\dataset"
OUTPUT_DIR = r"P:\Agri Analysis\backend\ml\disease_training\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 15 POPULATED CLASSES (background_other removed as per instructions)
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
    "rice_leaf_smut": 14
}

reverse_classes = {v: k for k, v in APPROVED_CLASSES.items()}

IMG_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

# ---------------------------------------------------------
# 2. Data Loading & Splitting
# ---------------------------------------------------------
def load_and_split_data():
    print(f"Reading inventory from {INVENTORY_CSV}...")
    df = pd.read_csv(INVENTORY_CSV)
    df = df[df['inclusion_status'] == 'INCLUDED']
    
    # Filter out any classes not in our 15 populated list
    df = df[df['canonical_class'].isin(APPROVED_CLASSES.keys())]
    df['local_path'] = df['image_path']
    df['class_idx'] = df['canonical_class'].map(APPROVED_CLASSES)
    
    df = df.drop_duplicates(subset=['sha256'])
    
    df['is_field'] = df['source_dataset'].apply(lambda x: 'PlantVillage' not in str(x))
    
    field_df = df[df['is_field']]
    lab_df = df[~df['is_field']]
    
    # Lab Split: 80% Train, 10% Val, 10% Test
    lab_train_val, lab_test = train_test_split(lab_df, test_size=0.1, stratify=lab_df['class_idx'], random_state=42)
    lab_train, lab_val = train_test_split(lab_train_val, test_size=0.1111, stratify=lab_train_val['class_idx'], random_state=42) 
    
    # Field Split: 60% Train, 10% Val, 30% Test
    try:
        field_train_val, field_test = train_test_split(field_df, test_size=0.3, stratify=field_df['class_idx'], random_state=42)
        field_train, field_val = train_test_split(field_train_val, test_size=0.1428, stratify=field_train_val['class_idx'], random_state=42)
    except ValueError:
        field_train_val, field_test = train_test_split(field_df, test_size=0.3, random_state=42)
        field_train, field_val = train_test_split(field_train_val, test_size=0.1428, random_state=42)
        
    train_df = pd.concat([lab_train, field_train])
    val_df = pd.concat([lab_val, field_val])
    test_df = pd.concat([lab_test, field_test])
    
    # Export the inventory used for training
    df.to_csv(os.path.join(OUTPUT_DIR, 'dataset_inventory.csv'), index=False)
    
    return train_df, val_df, test_df, df

# ---------------------------------------------------------
# 3. Dataset & Dataloaders
# ---------------------------------------------------------
class DiseaseDataset(Dataset):
    def __init__(self, df, transform=None):
        self.df = df.reset_index(drop=True)
        self.transform = transform
        
    def __len__(self):
        return len(self.df)
        
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        image = Image.open(row['local_path']).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, row['class_idx']

def create_dataloaders(train_df, val_df, test_df, batch_size=16):
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.8, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
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
    
    # CALCULATE WEIGHTS FROM TRAINING SET ONLY
    class_counts = train_df['class_idx'].value_counts().sort_index()
    total = sum(class_counts)
    class_weights = [total / class_counts[i] if i in class_counts else 1.0 for i in range(len(APPROVED_CLASSES))]
    class_weights_tensor = torch.FloatTensor(class_weights)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    
    return train_loader, val_loader, test_loader, class_weights_tensor

# ---------------------------------------------------------
# 4. Training
# ---------------------------------------------------------
import time

def train_model(train_loader, val_loader, class_weights_tensor, batch_size):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
    for param in model.parameters():
        param.requires_grad = False
    for param in model.features[-2:].parameters():
        param.requires_grad = True
        
    num_ftrs = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(num_ftrs, len(APPROVED_CLASSES))
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor.to(device))
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)
    
    scaler = torch.amp.GradScaler() 
    
    num_epochs = 15
    best_val_loss = float('inf')
    patience = 4
    patience_counter = 0
    
    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': [], 'learning_rate': [], 'duration': []}
    
    for epoch in range(num_epochs):
        start_time = time.time()
        model.train()
        running_loss, running_corrects = 0.0, 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            
            with torch.amp.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            
            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
        train_loss = running_loss / len(train_loader.dataset)
        train_acc = running_corrects.double() / len(train_loader.dataset)
        
        model.eval()
        val_loss, val_corrects = 0.0, 0
        all_val_labels, all_val_probs = [], []
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                with torch.amp.autocast(device_type='cuda' if torch.cuda.is_available() else 'cpu'):
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
        
        current_lr = optimizer.param_groups[0]['lr']
        scheduler.step(val_loss)
        
        duration = time.time() - start_time
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc.item())
        history['val_acc'].append(val_acc.item())
        history['learning_rate'].append(current_lr)
        history['duration'].append(duration)
        
        print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | Time: {duration:.1f}s")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, 'best_disease_model.pth'))
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
    print("\nCalibrating LOW_CONFIDENCE threshold targeting FPR < 5%...")
    best_thresh = 0.50
    # Since there is no background class, we just analyze the confidence distribution 
    # of misclassified images. We want to reject a high proportion of misclassified images 
    # as 'low confidence' while keeping correct predictions.
    preds = np.argmax(val_probs, axis=1)
    max_probs = np.max(val_probs, axis=1)
    
    # We want False Positives (incorrect predictions) that surpass the threshold to be < 5% of total predictions
    for t in np.arange(0.95, 0.40, -0.05):
        accepted = max_probs >= t
        incorrect_accepted = np.sum((preds[accepted] != val_labels[accepted]))
        fpr = incorrect_accepted / len(val_labels) if len(val_labels) > 0 else 0
        if fpr < 0.05:
            best_thresh = t
            
    print(f"Confidence Threshold determined: {best_thresh:.2f} (FPR control)")
    return round(best_thresh, 2)

def evaluate_model(model, test_loader, test_df, threshold):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.load_state_dict(torch.load(os.path.join(OUTPUT_DIR, 'best_disease_model.pth')))
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
    
    acc = accuracy_score(all_labels, all_preds)
    mac_prec = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    mac_rec = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    mac_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    w_prec = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
    w_rec = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
    w_f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)
    
    per_class_prec = precision_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_rec = recall_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_f1 = f1_score(all_labels, all_preds, average=None, zero_division=0)
    
    supports = [np.sum(all_labels == i) for i in range(len(APPROVED_CLASSES))]
    
    lowest_f1 = min(per_class_f1)
    lowest_f1_class = reverse_classes[np.argmin(per_class_f1)]
    
    metrics_df = pd.DataFrame({
        'Class': [reverse_classes[i] for i in range(len(APPROVED_CLASSES))],
        'Support': supports,
        'Precision': per_class_prec,
        'Recall': per_class_rec,
        'F1_Score': per_class_f1
    })
    metrics_df.to_csv(os.path.join(OUTPUT_DIR, 'per_class_metrics.csv'), index=False)
    
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(12,12))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrix.png'))
    
    # Field Generalization (subset analysis)
    field_mask = test_df['is_field'].values
    if np.sum(field_mask) > 0:
        field_acc = accuracy_score(all_labels[field_mask], all_preds[field_mask])
        field_mac_f1 = f1_score(all_labels[field_mask], all_preds[field_mask], average='macro', zero_division=0)
        field_w_f1 = f1_score(all_labels[field_mask], all_preds[field_mask], average='weighted', zero_division=0)
        field_result = f"Count={np.sum(field_mask)} | Acc={field_acc:.4f} | MacF1={field_mac_f1:.4f} | WF1={field_w_f1:.4f}"
    else:
        field_result = "NOT_AVAILABLE"

    return acc, mac_prec, mac_rec, mac_f1, w_prec, w_rec, w_f1, lowest_f1, lowest_f1_class, field_result

# ---------------------------------------------------------
# 6. ONNX Export & PyTorch Match Verification
# ---------------------------------------------------------
def export_and_verify_onnx(model, test_loader):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    
    # Get a single batch for verification
    for inputs, labels in test_loader:
        sample_inputs = inputs.to(device)
        break
        
    onnx_path = os.path.join(OUTPUT_DIR, 'disease_classifier.onnx')
    
    torch.onnx.export(model, sample_inputs, onnx_path, 
                      export_params=True, opset_version=14, 
                      do_constant_folding=True, 
                      input_names=['input'], output_names=['output'],
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})
    
    try:
        onnx_model = onnx.load(onnx_path)
        onnx.checker.check_model(onnx_model)
        onnx_status = "SUCCESS (Valid Graph)"
    except Exception as e:
        return f"FAILED ({str(e)})", "FAIL"
        
    # Verify Inference Match
    ort_session = onnxruntime.InferenceSession(onnx_path, providers=['CPUExecutionProvider'])
    
    with torch.no_grad():
        pt_outputs = model(sample_inputs).cpu().numpy()
        
    ort_inputs = {ort_session.get_inputs()[0].name: sample_inputs.cpu().numpy()}
    ort_outputs = ort_session.run(None, ort_inputs)[0]
    
    # Check max difference
    max_diff = np.max(np.abs(pt_outputs - ort_outputs))
    match_status = "PASS" if max_diff < 1e-4 else f"FAIL (max diff: {max_diff:.6f})"
    
    return onnx_status, match_status

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    train_df, val_df, test_df, full_df = load_and_split_data()
    batch_size = 16
    success = False
    
    while batch_size >= 4 and not success:
        print(f"Attempting training with batch_size={batch_size}")
        try:
            train_loader, val_loader, test_loader, class_weights = create_dataloaders(train_df, val_df, test_df, batch_size=batch_size)
            model = train_model(train_loader, val_loader, class_weights, batch_size)
            success = True
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"CUDA OOM at batch_size={batch_size}. Reducing...")
                batch_size = batch_size // 2
                torch.cuda.empty_cache()
            else:
                raise e
                
    if not success:
        print("Training failed due to OOM.")
        exit(1)
        
    # Load validation probs for calibration
    val_probs = np.load(os.path.join(OUTPUT_DIR, 'val_probs.npy'))
    val_labels = np.load(os.path.join(OUTPUT_DIR, 'val_labels.npy'))
    threshold = calibrate_threshold(val_probs, val_labels)
    
    acc, m_p, m_r, m_f1, w_p, w_r, w_f1, low_f1, low_class, field_res = evaluate_model(model, test_loader, test_df, threshold)
    onnx_status, match_status = export_and_verify_onnx(model, test_loader)
    
    # Export metadata & preprocessing
    with open(os.path.join(OUTPUT_DIR, 'class_names.json'), 'w') as f:
        json.dump(reverse_classes, f, indent=4)
        
    with open(os.path.join(OUTPUT_DIR, 'preprocessing.json'), 'w') as f:
        json.dump({"size": IMG_SIZE, "mean": MEAN, "std": STD}, f, indent=4)
        
    ready_for_django = True
    limitations = []
    
    if acc < 0.70:
        ready_for_django = False
        limitations.append("Overall accuracy is too low.")
    if low_f1 < 0.40:
        ready_for_django = False
        limitations.append(f"Class {low_class} has unacceptably low F1 score ({low_f1:.2f}).")
    if match_status != "PASS" or not onnx_status.startswith("SUCCESS"):
        ready_for_django = False
        limitations.append("ONNX verification failed or predictions do not match PyTorch.")
        
    metadata = {
        "model_name": "KrushiSense Disease V1",
        "architecture": "MobileNetV3-Small",
        "total_unique_images": len(full_df),
        "number_of_classes": len(APPROVED_CLASSES),
        "train_count": len(train_df),
        "validation_count": len(val_df),
        "test_count": len(test_df),
        "overall_accuracy": acc,
        "macro_f1": m_f1,
        "weighted_f1": w_f1,
        "lowest_class_f1": low_f1,
        "low_confidence_threshold": threshold,
        "background_rejection_result": "NOT_AVAILABLE",
        "field_generalization_result": field_res,
        "onnx_verification_result": onnx_status,
        "onnx_pytorch_prediction_match": match_status,
        "model_ready_for_django_integration": ready_for_django,
        "date": datetime.now().isoformat()
    }
    with open(os.path.join(OUTPUT_DIR, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)
        
    # Generate final safety report
    report = f"""=================================================
DISEASE MODEL FINAL EVALUATION REPORT
=================================================

MODEL_NAME: KrushiSense Disease V1
TOTAL_UNIQUE_IMAGES: {len(full_df)}
NUMBER_OF_CLASSES: {len(APPROVED_CLASSES)}
TRAIN_COUNT: {len(train_df)}
VALIDATION_COUNT: {len(val_df)}
TEST_COUNT: {len(test_df)}

OVERALL_ACCURACY: {acc:.4f}
MACRO_PRECISION: {m_p:.4f}
MACRO_RECALL: {m_r:.4f}
MACRO_F1: {m_f1:.4f}
WEIGHTED_PRECISION: {w_p:.4f}
WEIGHTED_RECALL: {w_r:.4f}
WEIGHTED_F1: {w_f1:.4f}

LOWEST_CLASS_F1: {low_f1:.4f}
LOWEST_PERFORMING_CLASS: {low_class}

LOW_CONFIDENCE_THRESHOLD: {threshold:.2f}

BACKGROUND_CLASS_TRAINED: NO
BACKGROUND_REJECTION_RESULT: NOT_AVAILABLE

FIELD_GENERALIZATION_RESULT: {field_res}

ONNX_VERIFICATION_RESULT: {onnx_status}
ONNX_PYTORCH_PREDICTION_MATCH: {match_status}

DATASET_LICENSE_STATUS: PlantVillage (CC0), PlantDoc (Unverified), Rice (Unverified)

MODEL_LIMITATIONS:
{chr(10).join(limitations) if limitations else 'No severe immediate limitations identified based on test set alone.'}
- The model lacks a dedicated background/unknown class, relying entirely on the confidence threshold to reject non-leaf images.

FINAL_MODEL_SAFETY_ASSESSMENT:
{"APPROVED FOR DJANGO INTEGRATION" if ready_for_django else "FAILED CRITICAL SAFETY CHECKS - DO NOT INTEGRATE"}

MODEL_READY_FOR_DJANGO_INTEGRATION: {"YES" if ready_for_django else "NO"}
"""
    with open(os.path.join(OUTPUT_DIR, 'disease_model_final_evaluation_report.txt'), 'w') as f:
        f.write(report)

