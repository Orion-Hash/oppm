# Basic imports
import argparse
import requests

# Parsers
parser = argparse.ArgumentParser(description="OPPM: Onrion Private Package Manager")
subparser = parser.add_subparsers(dest="command")

install = subparser.add_parser("install", help="Install a package")
install.add_argument("package", type=str, help="Name of the package to install")

# Parse from the MAIN parser, not the subparser
args = parser.parse_args()
print(args)

# Install Functions
def get_json(name):
    BASE_URL = "https://raw.githubusercontent.com/Orion-Hash/oppm/main/packages"
    return f"{BASE_URL}/{name}/package.json"

def download_files(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from {url}")
    

if args.command == "install":
    print(f"Installing package: {args.package}")
    print(download_files(get_json(args.package)))