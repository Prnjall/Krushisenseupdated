import pandas as pd
import numpy as np
import shutil
from pathlib import Path
import os

script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent

# Step 1: Preserve everything
backup_ml_dir = script_dir / "data_backups"
backup_models_dir = backend_dir / "predictions" / "models" / "historical_backups"

backup_ml_dir.mkdir(exist_ok=True)
backup_models_dir.mkdir(exist_ok=True)

files_to_backup = [
    (script_dir / "data" / "crop_merged.csv", backup_ml_dir / "crop_merged_historical.csv"),
    (backend_dir / "predictions" / "models" / "crop_recommendation_model.pkl", backup_models_dir / "crop_recommendation_model_historical.pkl"),
    (backend_dir / "predictions" / "models" / "crop_recommendation_tuned.pkl", backup_models_dir / "crop_recommendation_tuned_historical.pkl"),
    (backend_dir / "predictions" / "models" / "scaler.pkl", backup_models_dir / "scaler_historical.pkl"),
]

for src, dest in files_to_backup:
    if src.exists():
        shutil.copy2(src, dest)
        print(f"Backed up {src.name} to {dest}")

# Step 3: Separate datasets
csv_path = script_dir / "data" / "crop_merged.csv"
output_orig_csv = script_dir / "dataset_original.csv"
output_mh_csv = script_dir / "dataset_maharashtra.csv"
output_manifest = script_dir / "dataset_source_manifest.csv"
output_report = script_dir / "dataset_separation_report.txt"

df = pd.read_csv(csv_path)

# Separate based on district being null
df_orig = df[df['district'].isna()].copy()
df_mh = df[df['district'].notna()].copy()

df_orig.to_csv(output_orig_csv, index=False)
df_mh.to_csv(output_mh_csv, index=False)

print(f"Saved {output_orig_csv.name} and {output_mh_csv.name}")

# Create manifest
orig_crops = sorted(df_orig['label'].unique().tolist())
mh_crops = sorted(df_mh['label'].unique().tolist())

manifest_data = [
    {
        "source": "Original",
        "file": "dataset_original.csv",
        "row_count": len(df_orig),
        "crop_count": len(orig_crops),
        "crop_names": "|".join(orig_crops)
    },
    {
        "source": "Maharashtra",
        "file": "dataset_maharashtra.csv",
        "row_count": len(df_mh),
        "crop_count": len(mh_crops),
        "crop_names": "|".join(mh_crops)
    }
]

pd.DataFrame(manifest_data).to_csv(output_manifest, index=False)

# Create report
with open(output_report, "w", encoding="utf-8") as f:
    def log(text=""):
        print(text)
        f.write(text + "\n")
        
    log("=== DATASET SEPARATION REPORT ===")
    log(f"Original dataset row count: {len(df_orig)}")
    log(f"Maharashtra dataset row count: {len(df_mh)}")
    log(f"Crop count in Original: {len(orig_crops)}")
    log(f"Crop count in Maharashtra: {len(mh_crops)}")
    
    only_orig = sorted(set(orig_crops) - set(mh_crops))
    only_mh = sorted(set(mh_crops) - set(orig_crops))
    both = sorted(set(orig_crops) & set(mh_crops))
    
    log(f"\nCrops UNIQUE to Original dataset: {', '.join(only_orig) if only_orig else 'None'}")
    log(f"\nCrops UNIQUE to Maharashtra dataset: {', '.join(only_mh) if only_mh else 'None'}")
    log(f"\nCrops appearing in BOTH datasets: {', '.join(both) if both else 'None'}")
    
    log("\nConfirmation: No numerical transformations (normalization, scaling, modification) were performed during this separation process. The values are exact copies of the original.")
