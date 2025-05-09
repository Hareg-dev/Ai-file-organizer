# app/sorter_app.py

import os
import shutil
import pickle
import pandas as pd
import streamlit as st

# --- Load the trained ML model and encoders ---
model_path = "app/model.pkl"
with open(model_path, "rb") as f:
    data = pickle.load(f)
    model = data["model"]
    ext_encoder = data["ext_encoder"]
    dest_encoder = data["dest_encoder"]

# --- Setup folders ---
UPLOAD_FOLDER = "uploads"
SORTED_FOLDER = "sorted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

# --- Streamlit UI ---
st.set_page_config(page_title="AI Media Sorter", layout="centered")
st.title(" AI Media Sorter (Streamlit Version)")
st.write("Upload a file and let the trained AI model predict where to sort it.")

uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # Save uploaded file
    save_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extract features
    name_len = len(os.path.splitext(uploaded_file.name)[0])
    size = os.path.getsize(save_path)
    ext = os.path.splitext(uploaded_file.name)[1][1:] or "none"

    # Predict destination folder
    try:
        ext_encoded = ext_encoder.transform([ext])[0]
        X = pd.DataFrame([[name_len, size, ext_encoded]], columns=["name_len", "size_bytes", "ext_encoded"])
        pred_encoded = model.predict(X)[0]
        category = dest_encoder.inverse_transform([pred_encoded])[0]
    except Exception:
        category = "unknown"

    # Move to sorted folder
    dest_folder = os.path.join(SORTED_FOLDER, category)
    os.makedirs(dest_folder, exist_ok=True)
    shutil.move(save_path, os.path.join(dest_folder, uploaded_file.name))

    st.success(f" File {uploaded_file.name} sorted into {category}")