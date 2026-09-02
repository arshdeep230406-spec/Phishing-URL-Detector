import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

from feature_extraction import extract_features


# Load dataset
print("Loading dataset...")

df = pd.read_csv("dataset/phishing_urls.csv")

print("Dataset loaded successfully!")
print("Total URLs:", len(df))


# Use URL and label columns
df = df[["URL", "label"]]


# Extract features
print("Extracting URL features...")

features = []

for url in df["URL"]:
    features.append(extract_features(url))

X = pd.DataFrame(features)
y = df["label"]


print("Feature extraction completed!")
print("Features used:")
print(X.columns.tolist())


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


print("Training Random Forest model...")


# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)


# Train model
model.fit(X_train, y_train)


# Make predictions
y_pred = model.predict(X_test)


# Evaluate model
accuracy = accuracy_score(y_test, y_pred)

print("\nModel Training Completed!")
print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Save model
joblib.dump(model, "model.pkl")

print("\nModel saved successfully as model.pkl")