# organize.py

import os
import shutil
import pickle
from datetime import datetime

import pandas as pd

# Load model and encoders
with open("models/model.pkl", "rb") as f:
    data = pickle.load(f)
    model = data["model"]
    ext_encoder = data["ext_encoder"]
    dest_encoder = data["dest_encoder"]

# Folder to scan
SOURCE_FOLDER = os.path.join(os.getcwd(), "unsorted")
os.makedirs(SOURCE_FOLDER, exist_ok=True)

# Go through each file in the source folder
for file_name in os.listdir(SOURCE_FOLDER):
    file_path = os.path.join(SOURCE_FOLDER, file_name)

    if os.path.isfile(file_path):
        name_len = len(os.path.splitext(file_name)[0])
        size = os.path.getsize(file_path)
        ext = os.path.splitext(file_name)[1][1:] or "none"

        # Encode extension safely
        try:
            ext_encoded = ext_encoder.transform([ext])[0]
        except ValueError:
            print(f"Unknown extension '{ext}' — skipping file.")
            continue

        # Predict destination
        X = pd.DataFrame([[name_len, size, ext_encoded]], columns=["name_len", "size_bytes", "ext_encoded"])
        pred_encoded = model.predict(X)[0]
        predicted_folder = dest_encoder.inverse_transform([pred_encoded])[0]

        # Move the file
        dest_path = os.path.join(os.getcwd(), predicted_folder)
        os.makedirs(dest_path, exist_ok=True)

        shutil.move(file_path, os.path.join(dest_path, file_name))
        print(f"Moved {file_name} → {predicted_folder}")

