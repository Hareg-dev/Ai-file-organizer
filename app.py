# app/app.py

import os
import shutil
import pickle
from flask import Flask, render_template, request, redirect, url_for

import pandas as pd

# Load ML model and encoders
model_path = "app/model.pkl"
with open(model_path, "rb") as f:
    data = pickle.load(f)
    model = data["model"]
    ext_encoder = data["ext_encoder"]
    dest_encoder = data["dest_encoder"]

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "app/uploads"
SORTED_FOLDER = "app/sorted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SORTED_FOLDER, exist_ok=True)

# Route: Home
@app.route("/")
def index():
    return render_template("index.html")

# Route: Upload file and process
@app.route("/upload", methods=["POST"])
def upload():
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return redirect(url_for("index"))

    # Save uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
    uploaded_file.save(filepath)

    # Feature extraction
    name_len = len(os.path.splitext(uploaded_file.filename)[0])
    size = os.path.getsize(filepath)
    ext = os.path.splitext(uploaded_file.filename)[1][1:] or "none"

    try:
        ext_encoded = ext_encoder.transform([ext])[0]
    except ValueError:
        category = "unknown"
    else:
        X = pd.DataFrame([[name_len, size, ext_encoded]], columns=["name_len", "size_bytes", "ext_encoded"])
        pred_encoded = model.predict(X)[0]
        category = dest_encoder.inverse_transform([pred_encoded])[0]

    # Move file to predicted folder
    dest_folder = os.path.join(SORTED_FOLDER, category)
    os.makedirs(dest_folder, exist_ok=True)
    shutil.move(filepath, os.path.join(dest_folder, uploaded_file.filename))

    return f"File '{uploaded_file.filename}' sorted into '{category}'!"

# Run server
if __name__ == "main":
    app.run(debug=True)