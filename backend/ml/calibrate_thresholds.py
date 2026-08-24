import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"
models_dir = script_dir.parent / "predictions" / "models"

df = pd.read_csv(csv_path)
feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
target_col = "label"

X = df[feature_cols]
y = df[target_col]

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

joblib.dump(scaler, models_dir / "scaler.pkl")
np.save(models_dir / "X_train_scaled.npy", X_train_scaled)

nn = NearestNeighbors(n_neighbors=5)
nn.fit(X_train_scaled)

distances, _ = nn.kneighbors(X_val_scaled)
nearest_distances = distances[:, 0]
mean_5_distances = distances.mean(axis=1)

print("--- 1-NEAREST DISTANCES ---")
print(f"  75th Percentile: {np.percentile(nearest_distances, 75):.4f}")
print(f"  90th Percentile: {np.percentile(nearest_distances, 90):.4f}")
print(f"  95th Percentile: {np.percentile(nearest_distances, 95):.4f}")
print(f"  99th Percentile: {np.percentile(nearest_distances, 99):.4f}")
print(f"  Max: {nearest_distances.max():.4f}")

print("\n--- MEAN 5-NEAREST DISTANCES ---")
print(f"  75th Percentile: {np.percentile(mean_5_distances, 75):.4f}")
print(f"  90th Percentile: {np.percentile(mean_5_distances, 90):.4f}")
print(f"  95th Percentile: {np.percentile(mean_5_distances, 95):.4f}")
print(f"  99th Percentile: {np.percentile(mean_5_distances, 99):.4f}")
print(f"  Max: {mean_5_distances.max():.4f}")
