# gui_manager.py

import os
import shutil
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd

# Load the ML model
with open("models/model.pkl", "rb") as f:
    data = pickle.load(f)
    model = data["model"]
    ext_encoder = data["ext_encoder"]
    dest_encoder = data["dest_encoder"]

class FileManagerApp:
    def init(self, root):
        self.root = root
        self.root.title("Smart File Manager")
        self.selected_folder = ""
        self.selected_file = ""

        # Layout
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.browse_btn = tk.Button(self.frame, text="📁 Browse Folder", command=self.select_folder)
        self.browse_btn.pack(pady=10)

        # Treeview
        self.tree = ttk.Treeview(self.frame, columns=("Name", "Size"), show="headings", height=15)
        self.tree.heading("Name", text="Filename")
        self.tree.heading("Size", text="Size (KB)")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_file_select)

        # Action buttons
        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=5)

        self.predict_btn = tk.Button(action_frame, text="🔮 Predict Folder", command=self.predict_folder)
        self.predict_btn.grid(row=0, column=0, padx=5)

        self.move_btn = tk.Button(action_frame, text="📂 Move File", command=self.move_file)
        self.move_btn.grid(row=0, column=1, padx=5)

        self.delete_btn = tk.Button(action_frame, text="🗑️ Delete File", command=self.delete_file)
        self.delete_btn.grid(row=0, column=2, padx=5)

        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.load_files(folder)

    def load_files(self, folder):
        self.tree.delete(*self.tree.get_children())
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                size = os.path.getsize(path) // 1024
                self.tree.insert("", "end", values=(file, size))

    def on_file_select(self, event):
        item = self.tree.selection()
        if item:
            self.selected_file = self.tree.item(item)["values"][0]

    def predict_folder(self):
        if not self.selected_file:
            messagebox.showwarning("No file selected", "Select a file first.")
            return

        full_path = os.path.join(self.selected_folder, self.selected_file)
        name_len = len(os.path.splitext(self.selected_file)[0])
        size = os.path.getsize(full_path)
        ext = os.path.splitext(self.selected_file)[1][1:] or "none"

        try:
            ext_encoded = ext_encoder.transform([ext])[0]
        except ValueError:
            self.status_label.config(text=f"⚠️ Unknown extension '{ext}'", fg="red")
            return

        X = pd.DataFrame([[name_len, size, ext_encoded]], columns=["name_len", "size_bytes", "ext_encoded"])
        prediction = model.predict(X)[0]
        folder = dest_encoder.inverse_transform([prediction])[0]
        self.status_label.config(text=f"🔮 Predicted Folder: {folder}", fg="green")

        # Store prediction in case user wants to move it
        self.predicted_folder = folder

    def move_file(self):
        if not self.selected_file:
            messagebox.showwarning("No file selected", "Select a file to move.")
            return
        if not hasattr(self, "predicted_folder"):
            messagebox.showinfo("No prediction", "Run 'Predict Folder' first.")
            return

        source = os.path.join(self.selected_folder, self.selected_file)
        dest_folder = os.path.join(self.selected_folder, self.predicted_folder)
        os.makedirs(dest_folder, exist_ok=True)

        shutil.move(source, os.path.join(dest_folder, self.selected_file))
        self.status_label.config(text=f"✅ Moved to {self.predicted_folder}", fg="blue")
        self.load_files(self.selected_folder)

    def delete_file(self):
        if not self.selected_file:
            messagebox.showwarning("No file selected", "Select a file to delete.")
            return

        full_path = os.path.join(self.selected_folder, self.selected_file)
        os.remove(full_path)
        self.status_label.config(text="🗑️ File deleted", fg="red")
        self.load_files(self.selected_folder)

if __name__ == "main":
    root = tk.Tk()
    app = FileManagerApp(root)
    root.geometry("700x500")
    root.mainloop()