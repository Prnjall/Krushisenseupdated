import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    balanced_accuracy_score, confusion_matrix
)

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"
model_path = script_dir.parent / "predictions" / "models" / "crop_recommendation_model.pkl"
output_txt_path = script_dir / "model_audit.txt"

with open(output_txt_path, "w", encoding="utf-8") as f:
    def write_and_print(text):
        print(text)
        f.write(text + "\n")

    write_and_print("--- CROP RECOMMENDATION MODEL AUDIT ---\n")
    
    # 1. Load dataset
    df = pd.read_csv(csv_path)
    write_and_print(f"Dataset successfully loaded from {csv_path.name}")
    
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    target_col = "label"
    
    X = df[feature_cols]
    y = df[target_col]
    
    # 2. Check basics
    write_and_print("\n--- 1. DATASET CHECKS ---")
    write_and_print(f"Shape: {df.shape}")
    write_and_print(f"Columns: {df.columns.tolist()}")
    write_and_print(f"Missing Values:\n{df.isnull().sum().to_string()}")
    
    dup_rows = df.duplicated().sum()
    write_and_print(f"Duplicate Rows (all columns): {dup_rows}")
    
    dup_features = X.duplicated().sum()
    write_and_print(f"Duplicate Feature Combinations (ignoring label): {dup_features}")
    
    # Duplicate features with different labels
    dup_diff_labels = 0
    dups_X = df[X.duplicated(keep=False)]
    if not dups_X.empty:
        unique_labels_per_feat = dups_X.groupby(feature_cols)[target_col].nunique()
        dup_diff_labels = (unique_labels_per_feat > 1).sum()
    write_and_print(f"Exact feature duplicates belonging to DIFFERENT labels: {dup_diff_labels}")
    
    write_and_print(f"\nNumber of samples per crop:\n{y.value_counts().to_string()}")
    
    write_and_print("\nMin/Max of Features:")
    for col in feature_cols:
        write_and_print(f"  {col}: Min = {df[col].min():.4f}, Max = {df[col].max():.4f}")
    
    # 3. Proper stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    
    # 4. Load existing model
    clf = joblib.load(model_path)
    
    # 5. Calculate Metrics
    y_train_pred = clf.predict(X_train)
    y_test_pred = clf.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_train_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    acc_gap = train_acc - test_acc
    
    precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
    bal_acc = balanced_accuracy_score(y_test, y_test_pred)
    
    write_and_print("\n--- 2. MODEL METRICS ---")
    write_and_print(f"Training Accuracy: {train_acc:.4f}")
    write_and_print(f"Test Accuracy: {test_acc:.4f}")
    write_and_print(f"Accuracy Gap: {acc_gap:.4f}")
    write_and_print(f"Precision (Weighted): {precision:.4f}")
    write_and_print(f"Recall (Weighted): {recall:.4f}")
    write_and_print(f"F1-Score (Weighted): {f1:.4f}")
    write_and_print(f"Balanced Accuracy: {bal_acc:.4f}")
    
    # 6. 5-Fold Stratified K-Fold Cross-Validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    # Using clone via cross_val_score to check generalization
    cv_scores = cross_val_score(clf, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    write_and_print(f"\n5-Fold CV Mean Accuracy: {cv_mean:.4f}")
    write_and_print(f"5-Fold CV Accuracy Std Dev: {cv_std:.4f}")
    
    # 7. Confusion Matrix
    cm = confusion_matrix(y_test, y_test_pred, labels=clf.classes_)
    write_and_print("\n--- 3. CONFUSION MATRIX ---")
    write_and_print(np.array_str(cm))
    
    # 8. Per-class Accuracy
    write_and_print("\n--- 4. PER-CLASS ACCURACY ---")
    cm_diag = cm.diagonal()
    cm_sum = cm.sum(axis=1)
    for i, cls in enumerate(clf.classes_):
        acc = cm_diag[i] / cm_sum[i] if cm_sum[i] > 0 else 0
        write_and_print(f"  {cls}: {acc:.4f}")
        
    # 9. Feature Importance
    write_and_print("\n--- 5. FEATURE IMPORTANCE ---")
    if hasattr(clf, "feature_importances_"):
        importances = clf.feature_importances_
        for col, imp in zip(feature_cols, importances):
            write_and_print(f"  {col}: {imp:.4f}")
    else:
        write_and_print("  Model does not have feature_importances_ attribute.")
        
    # 10. and 11. Overfitting and data leakage analysis
    write_and_print("\n--- 6. DATA LEAKAGE & OVERFITTING ANALYSIS ---")
    if dup_features > 0:
        write_and_print("WARNING: Dataset contains duplicate feature rows.")
        write_and_print(f"Total rows: {len(df)}, Unique feature rows: {len(X.drop_duplicates())}")
        write_and_print("This can cause data leakage if identical samples end up in both training and testing sets, artificially inflating test accuracy and masking true overfitting.")
    
    # Extremely similar feature rows
    write_and_print("Extremely similar rows note: High percentage of exact duplicates likely masks real world variance.")
    
    summary_block = f"""
TRAINING ACCURACY: {train_acc:.4f}
TEST ACCURACY: {test_acc:.4f}
ACCURACY GAP: {acc_gap:.4f}
5-FOLD CV MEAN: {cv_mean:.4f}
5-FOLD CV STD: {cv_std:.4f}
BALANCED ACCURACY: {bal_acc:.4f}

EVIDENCE OF OVERFITTING:
"""
    if train_acc > 0.98 and acc_gap > 0.05:
        summary_block += "Yes. The model shows near-perfect training accuracy but a noticeable drop in test accuracy, indicating memorization."
    elif train_acc > 0.98 and acc_gap <= 0.05 and dup_features > 0:
        summary_block += "While the train-test accuracy gap is low, the near-perfect accuracy combined with exact duplicate features strongly suggests DATA LEAKAGE. The model is memorizing duplicate rows that leak across the train/test split. It is not generalizing well to unseen distinct data."
    else:
        summary_block += "The model does not show classic severe overfitting based on the accuracy gap, but evaluate leakage and balanced metrics carefully."
    
    write_and_print(summary_block)
