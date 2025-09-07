import json
import time
from pathlib import Path
from tkinter import filedialog, Tk

root = Tk()
root.withdraw()  # Hide the root window

print("Manifest creator. Version 1.0.0")

name = input("Package name: ")
time.sleep(0.5)
version = input("Version: ")
time.sleep(0.5)
description = input("Description: ")
time.sleep(0.5)

manifest = {
    "name": name,
    "version": version,
    "description": description,
    "oppm": {
        "format": 1
    }
}

folder_path_name = filedialog.askdirectory(title = "Select src folder")
folder_path = Path(folder_path_name)
file_path = folder_path / "manifest.json"

file_path.write_text(json.dumps(manifest, indent=4))
print(f"Manifest created at {file_path}")

input("Press Enter to exit...")