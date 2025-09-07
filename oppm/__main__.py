import argparse
import urllib.request
import json

BASE_URL = "https://raw.githubusercontent.com/Orion-Hash/oppm/main/packages"

# Create parser
parser = argparse.ArgumentParser(description="Oppm Command Line Interface")

# Create subparsers manager
subparsers = parser.add_subparsers(dest="command")

# Add install subparser
install_parser = subparsers.add_parser("install", help="Install a package")
install_parser.add_argument("package", help="Name of the package to install")

# Parse args AFTER commands are defined
args = parser.parse_args()

def GetManifest(url: str) -> dict:
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            manifest = json.loads(data)
            return manifest
    except Exception as e:
        print(f"Error fetching manifest: {e}. The package may not exist.")
        return {}
if args.command == "install":
    print(f"Installing {args.package}...")

    BUBBLE_POP_ELECTRIC = str.lower(args.package)

    PACKAGE_URL = f"{BASE_URL}/{BUBBLE_POP_ELECTRIC}/src/{BUBBLE_POP_ELECTRIC}/manifest.json"
    GetManifest(PACKAGE_URL)
