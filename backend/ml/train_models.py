import pandas as pd
from pathlib import Path

# Dynamically resolve dataset path
script_dir = Path(__file__).resolve().parent
csv_path = script_dir / "data" / "crop_merged.csv"

print("Resolved dataset path:", csv_path)
df = pd.read_csv(csv_path)

# Print first 5 rows
print("First 5 rows:")
print(df.head())

# Print column names
print("Column names:", df.columns.tolist())

# Print dataset shape
print("Dataset shape:", df.shape)

# Crop Recommendation Model Training
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Features and target
feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
target_col = "label"

X = df[feature_cols]
y = df[target_col]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
	X, y, test_size=0.2, random_state=42
)

# Train model
clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)

# Predict and print accuracy
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Crop Recommendation Model Accuracy: {acc * 100:.2f}%")

# Sample Prediction Test
sample_input = [[90, 42, 43, 20, 80, 6.5, 200]]  # Rice-like features
sample_pred = clf.predict(sample_input)[0]
sample_prob = clf.predict_proba(sample_input)
max_prob = max(sample_prob[0])
print(f"Sample Prediction Test:")
print(f"  Input: {sample_input}")
print(f"  Predicted Crop: {sample_pred}")
print(f"  Confidence (Probability): {max_prob * 100:.2f}%")

# Save trained model
import joblib

models_dir = script_dir.parent / "predictions" / "models"
models_dir.mkdir(parents=True, exist_ok=True)

crop_model_path = models_dir / "crop_recommendation_model.pkl"
joblib.dump(clf, crop_model_path)

# Yield Prediction Model Training
from sklearn.ensemble import RandomForestRegressor
import numpy as np

if "yield" in df.columns:
	y_reg = df["yield"]
	print("Yield column found in dataset.")
else:
	print("Yield column not found. Generating synthetic values.")
	np.random.seed(42)
	y_reg = np.random.uniform(10, 50, size=len(df))

X_reg = df[feature_cols]

X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
	X_reg, y_reg, test_size=0.2, random_state=42
)

reg = RandomForestRegressor(n_estimators=200, random_state=42)
reg.fit(X_reg_train, y_reg_train)

# Save yield prediction model
yield_model_path = models_dir / "yield_prediction_model.pkl"
joblib.dump(reg, yield_model_path)
print("Yield prediction model saved successfully:", yield_model_path)