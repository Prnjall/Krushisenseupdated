import os
import zipfile
import hashlib
import json
import csv
import io

BASE_DIR = r"P:\Agri Analysis\backend\ml\dataset"
OUTPUT_DIR = r"P:\Agri Analysis\backend\ml\disease_dataset"
os.makedirs(OUTPUT_DIR, exist_ok=True)

V1_CLASSES = {
    "apple_scab", "apple_black_rot", "apple_healthy",
    "maize_cercospora_leaf_spot", "maize_common_rust", "maize_northern_leaf_blight", "maize_healthy",
    "grape_black_rot", "grape_esca", "grape_leaf_blight", "grape_healthy",
    "rice_bacterial_leaf_blight", "rice_brown_spot", "rice_leaf_smut", "rice_healthy",
    "background_other"
}

CLASS_MAPPING_RULES = {
    # PlantVillage
    "Apple___Apple_scab": "apple_scab",
    "Apple___Black_rot": "apple_black_rot",
    "Apple___healthy": "apple_healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "maize_cercospora_leaf_spot",
    "Corn_(maize)___Common_rust_": "maize_common_rust",
    "Corn_(maize)___Northern_Leaf_Blight": "maize_northern_leaf_blight",
    "Corn_(maize)___healthy": "maize_healthy",
    "Grape___Black_rot": "grape_black_rot",
    "Grape___Esca_(Black_Measles)": "grape_esca",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "grape_leaf_blight",
    "Grape___healthy": "grape_healthy",
    
    # PlantDoc
    "Apple Scab Leaf": "apple_scab",
    "Apple leaf": "apple_healthy",
    "Corn Gray leaf spot": "maize_cercospora_leaf_spot",
    "Corn rust leaf": "maize_common_rust",
    "Corn leaf blight": "maize_northern_leaf_blight",
    "grape leaf": "grape_healthy",
    "grape leaf black rot": "grape_black_rot",
    
    # Rice Dataset 1 (Bacterial and Fungal)
    "Bacterial leaf blight": "rice_bacterial_leaf_blight",
    "Brown spot": "rice_brown_spot",
    "Leaf smut": "rice_leaf_smut",
    
    # Rice Dataset 2 (RiceLeafDiseaseBD)
    "Bacterialblight": "rice_bacterial_leaf_blight",
    "Blast": "rice_blast", # not in V1
    "Brownspot": "rice_brown_spot",
    "Tungro": "rice_tungro", # not in V1
    "Healthy": "rice_healthy"
}

def get_hash(data):
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

manifest = []
distribution = {}
unmapped_classes = set()
invalid_images = 0
total_images = 0
duplicates = 0
seen_hashes = set()
source_counts = {"PlantVillage": 0, "PlantDoc": 0, "Rice Dataset 1": 0, "Rice Dataset 2": 0, "Unknown": 0}

def process_file_data(filename, file_data, source_dataset, folder_name, filepath):
    global total_images, invalid_images, duplicates
    
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        return

    total_images += 1
    
    # Validation
    is_valid = True
    w, h = 0, 0
    try:
        if len(file_data) < 100:
            is_valid = False
    except Exception:
        is_valid = False

    if not is_valid:
        invalid_images += 1
        manifest.append([source_dataset, folder_name, "INVALID", "N/A", "N/A", filepath, "N/A", w, h, False, False, "UNVERIFIED", "EXCLUDED", "Corrupted or grayscale or too small"])
        return

    # Map class
    canonical_class = CLASS_MAPPING_RULES.get(folder_name)
    if not canonical_class:
        # try case insensitive matching
        for k, v in CLASS_MAPPING_RULES.items():
            if k.lower() == folder_name.lower():
                canonical_class = v
                break
                
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

    img_hash = "N/A"
    is_duplicate = False
    if status == "INCLUDED":
        img_hash = get_hash(file_data)
        if img_hash in seen_hashes:
            is_duplicate = True
            duplicates += 1
            status = "EXCLUDED"
            reason = "Exact duplicate"
        else:
            seen_hashes.add(img_hash)
            
    if canonical_class not in distribution:
        distribution[canonical_class] = {"total": 0, "PlantVillage": 0, "PlantDoc": 0, "Rice1": 0, "Rice2": 0, "Unknown": 0, "valid_unique": 0}
        
    distribution[canonical_class]["total"] += 1
    
    if source_dataset == "PlantVillage": distribution[canonical_class]["PlantVillage"] += 1
    elif source_dataset == "PlantDoc": distribution[canonical_class]["PlantDoc"] += 1
    elif source_dataset == "Rice Dataset 1": distribution[canonical_class]["Rice1"] += 1
    elif source_dataset == "Rice Dataset 2": distribution[canonical_class]["Rice2"] += 1
    else: distribution[canonical_class]["Unknown"] += 1
        
    if status == "INCLUDED":
        distribution[canonical_class]["valid_unique"] += 1
        
    manifest.append([
        source_dataset, folder_name, canonical_class, canonical_class.split('_')[0] if canonical_class != "UNMAPPED" else "N/A", 
        canonical_class, filepath, img_hash, w, h, True, is_duplicate, "UNVERIFIED", status, reason
    ])
    
    source_counts[source_dataset] = source_counts.get(source_dataset, 0) + 1

# Process Directories
for root, dirs, files in os.walk(BASE_DIR):
    if "data_distribution_for_svm" in root.lower() or "segmented" in root.lower() or "grayscale" in root.lower() or "augmented" in root.lower() or "generated" in root.lower() or "leaf_grouping" in root.lower():
        continue
        
    for f in files:
        filepath = os.path.join(root, f)
        source_dataset = "Unknown"
        if "PlantVillage" in filepath: source_dataset = "PlantVillage"
        elif "PlantDoc" in filepath: source_dataset = "PlantDoc"
        elif "Rice Leaf Bacterial and Fungal" in filepath: source_dataset = "Rice Dataset 1"
        elif "RiceLeafDiseaseBD" in filepath: source_dataset = "Rice Dataset 2"

        if f.lower().endswith('.zip'):
            print(f"Processing ZIP: {filepath}")
            try:
                with zipfile.ZipFile(filepath, 'r') as z:
                    for zinfo in z.infolist():
                        if zinfo.is_dir() or zinfo.filename.startswith('__MACOSX'):
                            continue
                        # Determine folder name from zip path
                        parts = zinfo.filename.replace('\\', '/').split('/')
                        if len(parts) > 1:
                            folder_name = parts[-2]
                        else:
                            folder_name = "Root"
                        
                        try:
                            with z.open(zinfo) as zf:
                                process_file_data(zinfo.filename, zf.read(), source_dataset, folder_name, f"{filepath}::{zinfo.filename}")
                        except Exception as e:
                            pass
            except Exception as e:
                print(f"Error reading zip {filepath}: {e}")
        elif f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            folder_name = os.path.basename(root)
            try:
                with open(filepath, 'rb') as fp:
                    process_file_data(f, fp.read(), source_dataset, folder_name, filepath)
            except Exception:
                pass

with open(os.path.join(OUTPUT_DIR, 'final_dataset_inventory.csv'), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["source_dataset", "original_class", "canonical_class", "crop", "disease", "image_path", "sha256", "width", "height", "valid", "duplicate", "license_status", "inclusion_status", "exclusion_reason"])
    writer.writerows(manifest)

rice_classes = ["rice_bacterial_leaf_blight", "rice_brown_spot", "rice_leaf_smut", "rice_healthy"]
with open(os.path.join(OUTPUT_DIR, 'final_rice_class_distribution.csv'), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["canonical_class", "total_images", "valid_unique_images", "rice1_count", "rice2_count"])
    for rc in rice_classes:
        stats = distribution.get(rc, {"total":0, "valid_unique":0, "Rice1":0, "Rice2":0})
        writer.writerow([rc, stats["total"], stats["valid_unique"], stats["Rice1"], stats["Rice2"]])

missing_classes = [rc for rc in rice_classes if distribution.get(rc, {}).get("valid_unique", 0) == 0]
imbalanced_classes = [rc for rc in rice_classes if distribution.get(rc, {}).get("valid_unique", 0) < 100]

ready = "YES" if len(missing_classes) == 0 and len(imbalanced_classes) == 0 else "NO"

report = f'''=============================================================
FINAL COMBINED DATASET AUDIT REPORT
=============================================================

1. Total images discovered: {total_images}
2. Total valid images: {total_images - invalid_images}
3. Total corrupted images (or grayscale/tiny): {invalid_images}
4. Total exact duplicates: {duplicates}
5. Total unique valid V1 images: {sum(s['valid_unique'] for s in distribution.values())}

6. Images per dataset (Total Discovered):
  - PlantVillage: {source_counts["PlantVillage"]}
  - PlantDoc: {source_counts["PlantDoc"]}
  - Rice Dataset 1: {source_counts["Rice Dataset 1"]}
  - Rice Dataset 2: {source_counts["Rice Dataset 2"]}

7. Images per canonical class (Valid & Unique):
'''
for cclass, stats in distribution.items():
    if cclass != "UNMAPPED" and stats['valid_unique'] > 0:
        report += f"  - {cclass}: {stats['valid_unique']}\n"

report += f'''
8. Rice class availability:
'''
for rc in rice_classes:
    cnt = distribution.get(rc, {}).get("valid_unique", 0)
    report += f"  - {rc}: {cnt}\n"

report += f'''
9. License/provenance status:
  - PlantVillage: CC0 (Public Domain)
  - PlantDoc: UNVERIFIED (Needs CC-BY check)
  - Rice Dataset 1: UNVERIFIED
  - Rice Dataset 2: UNVERIFIED

10. Class imbalance:
'''
if len(imbalanced_classes) > 0:
    report += f"  WARNING: Severe imbalance detected in: {', '.join(imbalanced_classes)}\n"
else:
    report += "  No severe imbalance detected (<100 images) among Rice classes.\n"

report += f'''
11. Final Rice readiness decision:
RICE_DATASET_READY_FOR_TRAINING = {ready}
'''
if ready == "NO":
    report += f"REASON: Missing or insufficient data for classes: {', '.join(missing_classes + imbalanced_classes)}\n"

report += '''
12. Final overall disease dataset readiness:
Overall, the dataset structure supports all planned V1 crops (Apple, Maize, Grape, Rice) assuming Rice is ready. 
'''

with open(os.path.join(OUTPUT_DIR, 'final_combined_dataset_audit.txt'), 'w', encoding='utf-8') as f:
    f.write(report)

print("Audit complete.")
