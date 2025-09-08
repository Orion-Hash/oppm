# Basic imports
import argparse
import requests
import json
from pathlib import Path
import pathlib
import os
import sys

print("=== DEBUG INFO ===")
print("Current folder:", os.getcwd())
print("Python location:", sys.executable)
print("Script location:", Path(__file__).resolve())
print("=== END DEBUG ===")
# Parsers
parser = argparse.ArgumentParser(description="OPPM: Onrion Private Package Manager")
subparser = parser.add_subparsers(dest="command")

install = subparser.add_parser("install", help="Install a package")
install.add_argument("package", type=str, help="Name of the package to install")

# Parse from the MAIN parser, not the subparser
args = parser.parse_args()


# Install Functions
def download(name):
    BASE_URL = "https://raw.githubusercontent.com/Orion-Hash/oppm/main/packages"
    URL = f"{BASE_URL}/{name}/package.json"

    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()

    # create a folder for this package
    package_dir = pathlib.Path("packages") / name
    package_dir.mkdir(parents=True, exist_ok=True)

    for filename in data["files"]:
        file_url = f"{BASE_URL}/{name}/{filename}"
        file_response = requests.get(file_url)

        if file_response.status_code == 200:
            file_path = package_dir / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)  # handles nested dirs

            # dump raw contents into file with same name
            file_path.write_bytes(file_response.content)

            print(f"Downloaded {filename} -> {file_path}")
        else:
            print(f"Failed to download {filename} from {file_url}")

    
    

if args.command == "install":
    print(f"Installing package: {args.package}")
    
    # Testing while I make this
    download(args.package)