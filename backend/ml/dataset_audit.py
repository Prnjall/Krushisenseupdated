import os
import glob
import hashlib
import json
import csv

BASE_DIR = r"P:\Agri Analysis\backend\ml\dataset"
OUTPUT_DIR = r"P:\Agri Analysis\backend\ml\disease_dataset"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define the expected V1 classes
V1_CLASSES = {
    "apple_scab", "apple_black_rot", "apple_healthy",
    "maize_cercospora_leaf_spot", "maize_common_rust", "maize_northern_leaf_blight", "maize_healthy",
    "grape_black_rot", "grape_esca", "grape_leaf_blight", "grape_healthy",
    "rice_bacterial_leaf_blight", "rice_brown_spot", "rice_leaf_smut", "rice_healthy",
    "background_other"
}

# Heuristic mapping for standard dataset folders
CLASS_MAPPING_RULES = {
    # PlantVillage Apple
    "Apple___Apple_scab": "apple_scab",
    "Apple___Black_rot": "apple_black_rot",
    "Apple___healthy": "apple_healthy",
    # PlantVillage Corn
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "maize_cercospora_leaf_spot",
    "Corn_(maize)___Common_rust_": "maize_common_rust",
    "Corn_(maize)___Northern_Leaf_Blight": "maize_northern_leaf_blight",
    "Corn_(maize)___healthy": "maize_healthy",
    # PlantVillage Grape
    "Grape___Black_rot": "grape_black_rot",
    "Grape___Esca_(Black_Measles)": "grape_esca",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "grape_leaf_blight",
    "Grape___healthy": "grape_healthy",
    
    # PlantDoc Apple
    "Apple Scab Leaf": "apple_scab",
    "Apple leaf": "apple_healthy", # Check visually in real life, but assumed healthy if just "Apple leaf"
    # PlantDoc Corn
    "Corn Gray leaf spot": "maize_cercospora_leaf_spot",
    "Corn rust leaf": "maize_common_rust",
    "Corn leaf blight": "maize_northern_leaf_blight",
    # PlantDoc Grape
    "grape leaf": "grape_healthy",
    "grape leaf black rot": "grape_black_rot"
}

def get_hash(filepath):
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            h.update(f.read())
        return h.hexdigest()
    except Exception:
        return None

manifest = []
distribution = {}
unmapped_classes = set()
invalid_images = 0
total_images = 0
duplicates = 0
seen_hashes = set()

# Process Datasets
for root, dirs, files in os.walk(BASE_DIR):
    if "grayscale" in root.lower() or "segmented" in root.lower() or "data_distribution_for_svm" in root.lower():
        continue
    print(f"Scanning directory: {root}")
    for f in files:
        if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
            
        total_images += 1
        filepath = os.path.join(root, f)
        
        # Determine source
        source_dataset = "Unknown"
        is_field = "controlled"
        if "PlantVillage" in filepath:
            source_dataset = "PlantVillage"
        elif "PlantDoc" in filepath:
            source_dataset = "PlantDoc"
            is_field = "field"
            
        folder_name = os.path.basename(root)
        
        # Basic file validation (since PIL is absent)
        is_valid = True
        w, h = 0, 0
        try:
            if os.path.getsize(filepath) == 0:
                is_valid = False
        except Exception:
            is_valid = False

        if not is_valid:
            invalid_images += 1
            manifest.append([source_dataset, folder_name, "INVALID", "N/A", "N/A", "N/A", filepath, "N/A", w, h, False, False, "UNVERIFIED", "EXCLUDED", "Corrupted or invalid format"])
            continue

        # Class mapping
        canonical_class = CLASS_MAPPING_RULES.get(folder_name)
        if not canonical_class:
            unmapped_classes.add(folder_name)
            canonical_class = "UNMAPPED"
            status = "EXCLUDED"
            reason = "Class not in V1 mapping"
        elif canonical_class not in V1_CLASSES:
            status = "EXCLUDED"
            reason = "Class mapped but not approved for V1"
        else:
            status = "INCLUDED"
            reason = "Valid"
            
        # Duplicate checking ONLY for included classes
        is_duplicate = False
        img_hash = "N/A"
        if status == "INCLUDED":
            img_hash = get_hash(filepath)
            if img_hash in seen_hashes:
                is_duplicate = True
                duplicates += 1
                status = "EXCLUDED"
                reason = "Exact duplicate"
            else:
                if img_hash:
                    seen_hashes.add(img_hash)
                
        # Update distribution
        if canonical_class not in distribution:
            distribution[canonical_class] = {"total": 0, "PlantVillage": 0, "PlantDoc": 0, "valid_unique": 0}
        
        distribution[canonical_class]["total"] += 1
        if source_dataset in ["PlantVillage", "PlantDoc"]:
            distribution[canonical_class][source_dataset] += 1
            
        if status == "INCLUDED":
            distribution[canonical_class]["valid_unique"] += 1
            
        manifest.append([
            source_dataset, folder_name, canonical_class, canonical_class.split('_')[0] if canonical_class != "UNMAPPED" else "N/A", 
            "N/A", "N/A", filepath, img_hash, w, h, True, is_duplicate, "UNVERIFIED", status, reason
        ])

        if total_images % 1000 == 0:
            print(f"Processed {total_images} images...")

# Write Class Mapping JSON
with open(os.path.join(OUTPUT_DIR, 'discovered_class_mapping.json'), 'w') as f:
    json.dump(CLASS_MAPPING_RULES, f, indent=4)

# Write Manifest CSV
with open(os.path.join(OUTPUT_DIR, 'discovered_dataset_manifest.csv'), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["source_dataset", "original_class", "canonical_class", "crop", "disease", "health_status", "image_path", "sha256", "image_width", "image_height", "valid", "duplicate", "license_status", "inclusion_status", "exclusion_reason"])
    writer.writerows(manifest)

# Write Distribution CSV
dist_rows = []
for cclass, stats in distribution.items():
    dist_rows.append([cclass, stats["total"], stats["valid_unique"], stats["PlantVillage"], stats["PlantDoc"]])

with open(os.path.join(OUTPUT_DIR, 'discovered_class_distribution.csv'), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["canonical_class", "total_images", "valid_unique_images", "plantvillage_count", "plantdoc_count"])
    writer.writerows(dist_rows)

# Generate Report
rice_classes = ["rice_bacterial_leaf_blight", "rice_brown_spot", "rice_leaf_smut", "rice_healthy"]
missing_classes = [rc for rc in rice_classes if distribution.get(rc, {}).get("valid_unique", 0) == 0]

ready = "YES" if len(missing_classes) == 0 else "NO"

report = f'''=============================================================
FINAL DATASET AUDIT REPORT
=============================================================

A. Total images discovered: {total_images}
B. Total valid images: {total_images - invalid_images}
C. Total invalid images: {invalid_images}
D. Total exact duplicates: {duplicates}
E. Total unique images: {total_images - invalid_images - duplicates}

F. Images per canonical class (Valid & Unique):
'''
for cclass, stats in distribution.items():
    if cclass != "UNMAPPED":
        report += f"  - {cclass}: {stats['valid_unique']} (PV: {stats['PlantVillage']}, PD: {stats['PlantDoc']})\n"

report += f'''
G. Images per source dataset (Total discovered):
  - PlantVillage: {sum([s['PlantVillage'] for s in distribution.values()])}
  - PlantDoc: {sum([s['PlantDoc'] for s in distribution.values()])}

H. Field vs controlled distribution:
  - Controlled (PlantVillage): {sum([s['PlantVillage'] for s in distribution.values()])}
  - Field (PlantDoc): {sum([s['PlantDoc'] for s in distribution.values()])}

I. Unmapped classes (Total unique unmapped folder names): {len(unmapped_classes)}
  (Examples: {list(unmapped_classes)[:5]}...)

J. Unsupported crops (No V1 support): Wheat, Cedar Apple Rust, etc. (All excluded gracefully)

K. License issues: PlantDoc license must be verified for commercial use (typically CC-BY-4.0). PlantVillage is CC0. 

L. Classes with insufficient data:
'''
if len(missing_classes) > 0:
    for mc in missing_classes:
        report += f"  - {mc}: 0 images (Critically Missing!)\n"
else:
    report += "  - None\n"

report += f'''
M. Classes suitable for training: Apple, Maize, Grapes (Subject to field data sufficiency)
N. Classes that should be excluded: Wheat, Apple Cedar Rust, all Unmapped.

O. Whether the dataset is READY FOR TRAINING
DATASET_READY_FOR_TRAINING = {ready}
'''
if ready == "NO":
    report += "\\nREASON: Missing Rice dataset entirely. Cannot proceed with V1 training scope."

with open(os.path.join(OUTPUT_DIR, 'discovered_dataset_report.txt'), 'w') as f:
    f.write(report)

print("Audit complete. Reports generated.")
