# cli_manager.py

import os
import argparse
import pandas as pd
import pickle
import shutil

from train_model import train_model  # Reuse your training logic
from collect_data import log_move    # Optional for --watch in future

# Load model
def load_model():
    with open("models/model.pkl", "rb") as f:
        data = pickle.load(f)
    return data["model"], data["ext_encoder"], data["dest_encoder"]

# Auto-organize files
def auto_organize(folder):
    model, ext_encoder, dest_encoder = load_model()

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        if os.path.isfile(path):
            name_len = len(os.path.splitext(file)[0])
            size = os.path.getsize(path)
            ext = os.path.splitext(file)[1][1:] or "none"

            try:
                ext_encoded = ext_encoder.transform([ext])[0]
            except ValueError:
                print(f"[SKIP] Unknown extension: {file}")
                continue

            X = pd.DataFrame([[name_len, size, ext_encoded]], columns=["name_len", "size_bytes", "ext_encoded"])
            pred_encoded = model.predict(X)[0]
            predicted_folder = dest_encoder.inverse_transform([pred_encoded])[0]

            dest_path = os.path.join(folder, predicted_folder)
            os.makedirs(dest_path, exist_ok=True)

            shutil.move(path, os.path.join(dest_path, file))
            print(f"[MOVE] {file} → {predicted_folder}")

# Argument parser
parser = argparse.ArgumentParser(description="Smart File Organizer CLI")
parser.add_argument("--auto", help="Auto-organize a folder", metavar="FOLDER")
parser.add_argument("--train", help="Retrain the model", action="store_true")
parser.add_argument("--log", help="Show last 10 logs", action="store_true")

args = parser.parse_args()

# Main logic
if args.auto:
    auto_organize(args.auto)

elif args.train:
    print("[TRAIN] Retraining model...")
    train_model()

elif args.log:
    log_path = "data/log.csv"
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        print(df.tail(10))
    else:
        print("No log file found.")

else:
    parser.print_help()