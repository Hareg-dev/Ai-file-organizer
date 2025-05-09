# collect_data.py

from watchdog.observers import Observer
import csv
from datetime import datetime
from watchdog.events import FileSystemEventHandler
import time
import logging
import os

logging.basicConfig(
    level=logging.INFO
)

# Define the folder you want to monitor
WATCH_FOLDER = os.path.join(os.getcwd(), "watch_folder")

# Create the folder if it doesn't exist
os.makedirs(WATCH_FOLDER, exist_ok=True)

# Define event handler class
class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"New file detected: {event.src_path}")

# Set up observer
event_handler = FileEventHandler()
observer = Observer()
observer.schedule(event_handler, WATCH_FOLDER, recursive=False)

# Start observing
print(f"Watching folder: {WATCH_FOLDER}")
observer.start()

try:
    while True:
        logging.info(time.sleep(1))
except KeyboardInterrupt:
    logging.warning(observer.stop())

observer.join()

LOG_FILE = os.path.join("data", "log.csv")
os.makedirs("data", exist_ok=True)

class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            extension = os.path.splitext(file_name)[1][1:]  # remove dot
            size = os.path.getsize(file_path)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Log format: [filename, extension, size_bytes, created_time]
            row = [file_name, extension, size, timestamp]

            with open(LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                if os.stat(LOG_FILE).st_size == 0:
                    logging.info(writer.writerow(["filename", "extension", "size_bytes", "timestamp"]))
                writer.writerow(row)

            logging.info(f"Logged: {file_name}")