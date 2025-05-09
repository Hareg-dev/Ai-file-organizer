# train_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Load data
df = pd.read_csv("log.csv")

# Preprocessing
df["name_len"] = df["filename"].apply(lambda x: len(os.path.splitext(x)[0]))
df["extension"] = df["extension"].fillna("none")

# Encode categorical features
ext_encoder = LabelEncoder()
dest_encoder = LabelEncoder()

df["ext_encoded"] = ext_encoder.fit_transform(df["extension"])
df["dest_encoded"] = dest_encoder.fit_transform(df["destination"])

# Features and label
X = df[["name_len", "size_bytes", "ext_encoded"]]
y = df["dest_encoded"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Optional: Print accuracy for fun
acc = model.score(X_test, y_test)
print(f"Model trained! Accuracy on test set: {acc:.2f}")

# Save the model + encoders
os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump({
        "model": model,
        "ext_encoder": ext_encoder,
        "dest_encoder": dest_encoder
    }, f)

print("Model and encoders saved to models/model.pkl")