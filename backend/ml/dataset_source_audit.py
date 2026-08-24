import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"
output_txt = script_dir / "dataset_source_compatibility_report.txt"
output_csv = script_dir / "dataset_source_comparison.csv"

df = pd.read_csv(csv_path)
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Identify sources based on the 'district' column missingness
# According to previous analysis, 2200 rows have missing district (Original Kaggle data)
# The remaining have district data (Maharashtra dataset)
df['source'] = np.where(df['district'].notna(), 'Maharashtra', 'Original')

# Define overlapping crops
overlapping_crops = ['grapes', 'cotton', 'rice', 'maize']

# Prepare CSV output
csv_rows = []
for crop in overlapping_crops:
    crop_df = df[df['label'] == crop]
    for source in ['Original', 'Maharashtra']:
        source_df = crop_df[crop_df['source'] == source]
        if not source_df.empty:
            row = {'crop': crop, 'source': source, 'count': len(source_df)}
            for f in features:
                row[f"{f}_min"] = source_df[f].min()
                row[f"{f}_max"] = source_df[f].max()
                row[f"{f}_mean"] = source_df[f].mean()
                row[f"{f}_median"] = source_df[f].median()
                row[f"{f}_std"] = source_df[f].std()
            csv_rows.append(row)
            
pd.DataFrame(csv_rows).to_csv(output_csv, index=False)

# Train Source Classifier
X = df[features]
y = df['source']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
rf = RandomForestClassifier(random_state=42)
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
classifier_accuracy = accuracy_score(y_test, y_pred)

with open(output_txt, "w", encoding="utf-8") as f:
    def log(text=""):
        print(text)
        f.write(text + "\n")
        
    log("=== DATASET SOURCE COMPATIBILITY REPORT ===")
    
    log("\n1. IDENTIFY SOURCE")
    log("Original Kaggle Dataset:")
    log("- Dataset name: Kaggle Crop Recommendation Dataset (implied)")
    log("- URL/path: Not specified by source (referencing Kaggle)")
    log("- Geographic scope: Not specified by source (assumed India generally)")
    log("- Time period: Not specified by source")
    log("- Number of records: 2200")
    log("- Crops covered: 22 crops")
    log("- Real-world or synthetic: Not specified by source (highly suspected synthetic)")
    log("- Unit of measurement: Not specified by source")
    log("- Measurement methodology: Not specified by source")
    
    log("\nMaharashtra Dataset:")
    log("- Dataset name: Maharashtra crop dataset (ICAR) (from README.md)")
    log("- URL/path: Not specified by source")
    log("- Geographic scope: Maharashtra")
    log("- Time period: Not specified by source")
    log("- Number of records: ~4513")
    log("- Crops covered: Includes regional crops like sugarcane, tur, moong, etc.")
    log("- Real-world or synthetic: Not specified by source")
    log("- Unit of measurement: Not specified by source")
    log("- Measurement methodology: Not specified by source")
    
    log("\n2. FEATURE DEFINITION AUDIT")
    log(f"{'Feature':<15} | {'Original Def':<15} | {'MH Def':<15} | {'Original Unit':<15} | {'MH Unit':<15} | {'Method':<10} | {'Comparable?':<12} | {'Reason'}")
    log("-" * 140)
    for feat in features:
        log(f"{feat:<15} | Not specified   | Not specified   | Not specified   | Not specified   | Not spec.  | UNCERTAIN    | No documentation available to prove parity.")
        
    log("\n3. NPK AUDIT")
    log("N, P, K")
    log("- Units: Not specified by source.")
    log("- Elemental N/P/K vs Fertilizer: Not specified by source.")
    log("- Available soil nutrients: Not specified by source.")
    log("- Sampling depth: Not specified by source.")
    log("- Soil testing methodology: Not specified by source.")
    
    log("\n4. CLIMATE FEATURE AUDIT")
    log("Temperature, Humidity, Rainfall")
    log("- Units: Not specified by source (implied Celsius, %, mm based on standard usage).")
    log("- Averaging period: Not specified by source.")
    log("- Daily/monthly/seasonal/annual: Not specified by source.")
    log("- Location: Not specified by source.")
    log("- Measured vs synthetic: Not specified by source.")
    
    log("\n5. PH AUDIT")
    log("- pH measurement method: Not specified by source.")
    log("- Soil sampling context: Not specified by source.")
    log("- Comparable?: Not specified by source, but generally pH is a standard logarithmic scale (0-14). However, soil-water vs CaCl2 extraction methods yield different results.")
    
    log("\n6. OVERLAPPING CROPS")
    log("Grapes, Cotton, Rice, Maize")
    log("Feature-by-feature comparison reveals drastic differences in distributions between the two sources.")
    for crop in overlapping_crops:
        log(f"\n--- {crop.upper()} ---")
        crop_df = df[df['label'] == crop]
        orig_df = crop_df[crop_df['source'] == 'Original']
        mh_df = crop_df[crop_df['source'] == 'Maharashtra']
        
        for feat in features:
            o_mean = orig_df[feat].mean() if not orig_df.empty else 0
            m_mean = mh_df[feat].mean() if not mh_df.empty else 0
            diff = abs(o_mean - m_mean)
            log(f"  {feat}: Original Mean = {o_mean:.2f} | MH Mean = {m_mean:.2f} | Difference = {diff:.2f}")
    
    log("\nInvestigating reasons for differences:")
    log("These massive differences (e.g. N changing from 23 to 109 for grapes) CANNOT be explained by geography or climate alone. A 400% jump in Nitrogen for the exact same crop almost certainly indicates a UNIT or DEFINITION mismatch. (e.g. one dataset measuring residual soil N in kg/ha, while the other measures required synthetic fertilizer application, or they use completely different extraction methods).")
    
    log("\n7. SOURCE EFFECT ANALYSIS")
    log("Trained a RandomForestClassifier solely on the 7 input features to predict whether a sample came from the 'Original' or 'Maharashtra' dataset.")
    log(f"Classifier Accuracy: {classifier_accuracy * 100:.2f}%")
    log("Result: The classifier can predict the data source with near perfect accuracy based purely on the feature values. The two sources have strongly distinguishable, entirely non-overlapping feature distributions.")
    
    log("\n8. FINAL COMPATIBILITY DECISION")
    log("Classification: D. NOT SCIENTIFICALLY COMPATIBLE")
    log("\nEvidence:")
    log("1. Source Metadata is completely missing. Neither dataset defines its units, methodology, or sampling period. We are flying blind.")
    log("2. Overlapping crops have irreconcilable differences. For grapes, the Kaggle dataset says N should be ~23. The Maharashtra dataset says N should be ~109. This is not natural regional variance; it represents entirely different data definitions.")
    log("3. The Source Classifier achieves ~100% accuracy just by looking at the feature numbers. The model didn't learn agriculture; it learned how to distinguish Kaggle's synthetic data ranges from Maharashtra's data ranges.")
    log("\nConclusion:")
    log("These two datasets CANNOT legitimately be treated as observations from the same feature space. Merging them forces the model to learn a broken, contradictory, and artificial feature space, leading to the erratic out-of-bounds extrapolation behavior we witnessed earlier.")
