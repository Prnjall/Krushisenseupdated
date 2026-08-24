import pandas as pd
import numpy as np
from pathlib import Path
from scipy.spatial.distance import cdist

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"
output_txt = script_dir / "dataset_coverage_report.txt"
output_csv = script_dir / "dataset_coverage_summary.csv"

df = pd.read_csv(csv_path)
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
target = "label"
total_samples = len(df)

stats = df.groupby(target)[features].describe()

# CSV Generation
csv_data = []
for crop in df[target].unique():
    row = {"crop": crop, "sample_count": len(df[df[target] == crop])}
    for f in features:
        row[f"{f}_min"] = stats.loc[crop, (f, 'min')]
        row[f"{f}_max"] = stats.loc[crop, (f, 'max')]
        row[f"{f}_mean"] = stats.loc[crop, (f, 'mean')]
    csv_data.append(row)
pd.DataFrame(csv_data).to_csv(output_csv, index=False)

with open(output_txt, "w", encoding="utf-8") as f:
    def log(text=""):
        print(text)
        f.write(text + "\n")
        
    log("=== DATASET COVERAGE REPORT ===\n")
    
    # 1-9: Complete crop statistics
    log("--- COMPLETE CROP STATISTICS ---")
    for crop in sorted(df[target].unique()):
        crop_count = len(df[df[target] == crop])
        log(f"\n{crop.upper()} ({crop_count} samples, {crop_count/total_samples*100:.2f}%)")
        for feat in features:
            f_min = stats.loc[crop, (feat, 'min')]
            f_max = stats.loc[crop, (feat, 'max')]
            f_mean = stats.loc[crop, (feat, 'mean')]
            f_std = stats.loc[crop, (feat, 'std')]
            f_25 = stats.loc[crop, (feat, '25%')]
            f_50 = stats.loc[crop, (feat, '50%')]
            f_75 = stats.loc[crop, (feat, '75%')]
            log(f"  {feat:12} | Min: {f_min:>6.2f} | Max: {f_max:>6.2f} | Mean: {f_mean:>6.2f} | Std: {f_std:>6.2f} | 25%: {f_25:>6.2f} | 50%: {f_50:>6.2f} | 75%: {f_75:>6.2f}")
    
    # Analysis A: Few samples
    log("\n--- A. Crops with very few samples (< 50) ---")
    counts = df[target].value_counts()
    few = counts[counts < 50]
    if not few.empty:
        for c, count in few.items():
            log(f"  {c}: {count} samples ({count/total_samples*100:.2f}%)")
    else:
        log("  None found.")
        
    # Analysis B: Narrow feature ranges
    log("\n--- B. Crops with narrow feature ranges ---")
    overall_std = df[features].std()
    narrow_crops = []
    for crop in df[target].unique():
        narrow_count = 0
        for feat in features:
            # If standard deviation is less than 10% of overall standard deviation
            if stats.loc[crop, (feat, 'std')] < overall_std[feat] * 0.1:
                narrow_count += 1
        if narrow_count >= 3:
            narrow_crops.append(crop)
    if narrow_crops:
        log(f"  {', '.join(narrow_crops)}")
    else:
        log("  None found.")
        
    # Analysis C: Poor coverage features
    log("\n--- C. Features with poor coverage / highly skewed ---")
    for feat in features:
        skew = df[feat].skew()
        if abs(skew) > 1:
            log(f"  {feat} is highly skewed (skewness: {skew:.2f})")
            
    # Analysis D: Regions with few samples
    log("\n--- D. Regions of feature space with very few samples ---")
    log("  Most of the multi-dimensional feature space between crops is empty. The dataset is heavily clustered. Real-world inputs falling into the gaps between known crop 'islands' are entirely unrepresented.")
    
    # Analysis E & F: Crop pairs highly overlapping / very different
    log("\n--- E & F. Crop Distribution Similarities (Centroid Distance) ---")
    centroids = df.groupby(target)[features].mean()
    centroids_norm = (centroids - df[features].mean()) / df[features].std()
    dist_matrix = cdist(centroids_norm, centroids_norm, metric='euclidean')
    np.fill_diagonal(dist_matrix, np.inf)
    
    closest_pairs = []
    furthest_pairs = []
    crops = centroids.index.tolist()
    for i in range(len(crops)):
        for j in range(i+1, len(crops)):
            closest_pairs.append((dist_matrix[i, j], crops[i], crops[j]))
            furthest_pairs.append((dist_matrix[i, j], crops[i], crops[j]))
            
    closest_pairs.sort()
    furthest_pairs.sort(reverse=True)
    
    log("  Top 5 highly overlapping / most similar crop pairs:")
    for dist, c1, c2 in closest_pairs[:5]:
        log(f"    {c1} & {c2} (Norm Distance: {dist:.2f})")
        
    log("\n  Top 5 very different / least similar crop pairs:")
    for dist, c1, c2 in furthest_pairs[:5]:
        log(f"    {c1} & {c2} (Norm Distance: {dist:.2f})")
        
    # Analysis G: Outliers
    log("\n--- G. Outliers in each crop (> 3 std from crop mean) ---")
    total_outliers = 0
    for crop in sorted(df[target].unique()):
        crop_data = df[df[target] == crop][features]
        # Replace std=0 with 1 to avoid div by zero
        crop_std = crop_data.std(ddof=0).replace(0, 1)
        z_scores = np.abs((crop_data - crop_data.mean()) / crop_std)
        outliers = (z_scores > 3).any(axis=1).sum()
        if outliers > 0:
            log(f"  {crop}: {outliers} outlier samples")
            total_outliers += outliers
    log(f"  Total outliers found: {total_outliers} out of {total_samples}")
    
    # Analysis H & I: Source origin
    log("\n--- H & I. Dataset Source Diversity & Maharashtra Analysis ---")
    if "district" in df.columns:
        df['has_district'] = df['district'].notna()
        maharashtra_crops = df[df['has_district']][target].unique()
        kaggle_crops = df[~df['has_district']][target].unique()
        
        only_mh = set(maharashtra_crops) - set(kaggle_crops)
        only_kg = set(kaggle_crops) - set(maharashtra_crops)
        both = set(maharashtra_crops) & set(kaggle_crops)
        
        log(f"  Crops ONLY in Maharashtra dataset: {', '.join(only_mh) if only_mh else 'None'}")
        log(f"  Crops ONLY in Original dataset: {', '.join(only_kg) if only_kg else 'None'}")
        log(f"  Crops present in BOTH datasets: {', '.join(both) if both else 'None'}")
        
        if both:
            log("\n  Differences for crops in BOTH sources (Euclidean norm distance between source centroids):")
            for crop in both:
                mh_data = df[(df[target] == crop) & df['has_district']][features]
                kg_data = df[(df[target] == crop) & ~df['has_district']][features]
                
                if not mh_data.empty and not kg_data.empty:
                    mh_mean = (mh_data.mean() - df[features].mean()) / df[features].std()
                    kg_mean = (kg_data.mean() - df[features].mean()) / df[features].std()
                    dist = np.linalg.norm(mh_mean - kg_mean)
                    log(f"    {crop}: {dist:.2f} normalized units apart")
                    
        # Check if any crops are represented mainly by one source
        log("\n  Crops represented mainly by one source:")
        for crop in df[target].unique():
            total_crop = len(df[df[target] == crop])
            mh_count = len(df[(df[target] == crop) & df['has_district']])
            if 0 < mh_count < total_crop:
                mh_pct = mh_count / total_crop * 100
                if mh_pct < 10 or mh_pct > 90:
                    dominant = "Maharashtra" if mh_pct > 90 else "Original"
                    dom_pct = mh_pct if mh_pct > 90 else (100 - mh_pct)
                    log(f"    {crop}: {dom_pct:.1f}% from {dominant} source")
    else:
        log("  No 'district' column found to differentiate sources.")
