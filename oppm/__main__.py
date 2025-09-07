import argparse
import sys

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

if args.command == "install":
    print(f"Installing {args.package}...")

BUBBLE_POP_ELECTRIC = str.lower(args.package)

PACKAGE_URL = f"{BASE_URL}/{BUBBLE_POP_ELECTRIC}/src/manifest.json"
print(PACKAGE_URL)