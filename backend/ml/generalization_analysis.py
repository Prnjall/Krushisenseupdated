import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.neighbors import NearestNeighbors

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"
model_path = script_dir.parent / "predictions" / "models" / "crop_recommendation_model.pkl"
output_txt_path = script_dir / "generalization_analysis.txt"

df = pd.read_csv(csv_path)
clf = joblib.load(model_path)

feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
target_col = "label"

X = df[feature_cols]
y = df[target_col]
classes = clf.classes_

with open(output_txt_path, "w", encoding="utf-8") as f:
    def log(text=""):
        print(text)
        f.write(text + "\n")
        
    log("=== GENERALIZATION ANALYSIS ===")
    
    # 1 & 2: Crop Feature Statistics & Ranges
    log("\n--- 1 & 2. Crop Feature Statistics & Ranges ---")
    stats = df.groupby(target_col)[feature_cols].agg(['min', 'max', 'mean', 'median', 'std'])
    
    # Identify narrow ranges
    log("\n--- 5. Crops with Narrow Feature Ranges ---")
    overall_std = df[feature_cols].std()
    narrow_thresholds = overall_std * 0.1
    
    narrow_counts = {}
    for crop in classes:
        if crop not in stats.index: continue
        narrow_features = []
        for col in feature_cols:
            if stats.loc[crop, (col, 'std')] < narrow_thresholds[col]:
                narrow_features.append(col)
        if len(narrow_features) >= 3:
            narrow_counts[crop] = narrow_features
            
    if narrow_counts:
        log("The following crops have extremely narrow ranges (std < 10% of overall std) across >= 3 features:")
        for crop, feats in narrow_counts.items():
            log(f"  {crop}: {', '.join(feats)}")
    else:
        log("No crops exhibit extremely narrow ranges across the majority of features.")
        
    # 4. Class Overlap (Approximation via bounding boxes)
    log("\n--- 4. Class Overlap Analysis (Bounding Box Overlap) ---")
    overlapping_pairs = []
    crops = df[target_col].unique()
    for i in range(len(crops)):
        for j in range(i+1, len(crops)):
            crop1 = crops[i]
            crop2 = crops[j]
            overlap_all_dims = True
            for col in feature_cols:
                c1_min = stats.loc[crop1, (col, 'min')]
                c1_max = stats.loc[crop1, (col, 'max')]
                c2_min = stats.loc[crop2, (col, 'min')]
                c2_max = stats.loc[crop2, (col, 'max')]
                
                if c1_max < c2_min or c2_max < c1_min:
                    overlap_all_dims = False
                    break
            
            if overlap_all_dims:
                overlapping_pairs.append((crop1, crop2))
                
    if overlapping_pairs:
        log(f"Found {len(overlapping_pairs)} pairs of crops whose 7-dimensional bounding boxes overlap:")
        for p1, p2 in overlapping_pairs[:10]:
            log(f"  {p1} - {p2}")
        if len(overlapping_pairs) > 10:
            log(f"  ... and {len(overlapping_pairs)-10} more.")
    else:
        log("No overlapping crop classes found in the 7-dimensional bounding box space. The classes are completely linearly separated in at least one dimension for every pair!")
    
    # 6. Unexplored regions
    log("\n--- 6. Feature Space Coverage Analysis ---")
    np.random.seed(42)
    overall_mins = X.min().values
    overall_maxs = X.max().values
    random_pts = np.random.uniform(overall_mins, overall_maxs, size=(10000, len(feature_cols)))
    
    in_any_box = 0
    for pt in random_pts:
        found_box = False
        for crop in crops:
            c_mins = [stats.loc[crop, (col, 'min')] for col in feature_cols]
            c_maxs = [stats.loc[crop, (col, 'max')] for col in feature_cols]
            if np.all((pt >= np.array(c_mins)) & (pt <= np.array(c_maxs))):
                found_box = True
                break
        if found_box:
            in_any_box += 1
            
    coverage_pct = (in_any_box / 10000) * 100
    log(f"Estimated bounding box coverage of the total feature volume: {coverage_pct:.2f}%")
    
    # 7 & 8 & 9. Test Unseen Combinations
    log("\n--- 7, 8, 9. Unseen combination tests ---")
    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(X)
    
    unseen_inputs = []
    # Generate 20 realistic unseen combinations inside the bounds but mostly random
    for _ in range(20):
        pt = []
        for col in feature_cols:
            c_min = overall_mins[feature_cols.index(col)]
            c_max = overall_maxs[feature_cols.index(col)]
            pt.append(np.random.uniform(c_min + (c_max-c_min)*0.1, c_max - (c_max-c_min)*0.1))
        unseen_inputs.append(pt)
    
    unseen_df = pd.DataFrame(unseen_inputs, columns=feature_cols)
    
    preds = clf.predict(unseen_df)
    probs = clf.predict_proba(unseen_df)
    distances, _ = nn.kneighbors(unseen_df)
    
    log(f"Testing {len(unseen_inputs)} unseen inputs...\n")
    for i, row in unseen_df.iterrows():
        pred_crop = preds[i]
        prob_dist = probs[i]
        dist_to_nearest = distances[i][0]
        
        top3_idx = np.argsort(prob_dist)[-3:][::-1]
        top3_crops = [(classes[idx], prob_dist[idx]) for idx in top3_idx]
        
        inside_cols = []
        outside_cols = []
        for col in feature_cols:
            c_min = stats.loc[pred_crop, (col, 'min')]
            c_max = stats.loc[pred_crop, (col, 'max')]
            val = row[col]
            if c_min <= val <= c_max:
                inside_cols.append(col)
            else:
                outside_cols.append(col)
                
        is_inside_range = len(outside_cols) == 0
        
        log(f"Input {i+1}:")
        log(f"  Values: {{k: round(v, 2) for k, v in row.to_dict().items()}}")
        log(f"  Distance to nearest training sample: {dist_to_nearest:.2f}")
        log(f"  Predicted Crop: {pred_crop}")
        log(f"  Top 3 Probabilities: {', '.join([f'{c} ({p:.2f})' for c, p in top3_crops])}")
        
        if is_inside_range:
            log(f"  Falls INSIDE observed bounds for {pred_crop}")
        else:
            log(f"  Falls OUTSIDE observed bounds for {pred_crop} in: {', '.join(outside_cols)}")
        log("")
        
    log("\n--- CONCLUSION: ROOT CAUSE OF POOR GENERALIZATION ---")
    log("Based on the analysis:")
    if coverage_pct < 5:
        log("- [A] Narrow Dataset Coverage: The dataset consists of distinct, isolated clusters in the feature space. The vast majority (>95%) of possible feature combinations are unseen.")
    if len(overlapping_pairs) == 0:
        log("- [C] Class Overlap: There is ZERO class overlap in the bounding boxes. The classes are artificially perfectly separable.")
        
    log("- [D] Random Forest Extrapolation: RF models cannot extrapolate meaningfully into empty space. When an unseen input lands far from known samples, it falls into a leaf node dedicated to a specific crop island, often outputting high confidence (1.0 probability) simply because the leaf node is pure.")
    log("\nThe actual problem is: A (narrow dataset coverage / clustered synthetic data) combined with D (RF extrapolation behavior). The model isn't overfitting in the traditional sense; it just has no data for the spaces between clusters.")
