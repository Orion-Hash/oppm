import argparse
import urllib.request
import json
import os

BASE_URL = "https://raw.githubusercontent.com/Orion-Hash/oppm/main/packages"
INSTALL_DIR = os.path.join(os.getcwd(), "packages_installed")  # per-project installs


def GetManifest(url: str) -> dict:
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            manifest = json.loads(data)
            return manifest
    except Exception as e:
        print(f"Error fetching manifest: {e}. The package may not exist.")
        return {}


def DownloadFile(url: str, dest: str):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(url) as response:
        data = response.read()
        with open(dest, "wb") as f:
            f.write(data)
    print(f"Downloaded → {dest}")


def pick_latest_version(files: dict) -> str:
    # files = { "1.0.0": "logger-1.0.0.zip", ... }
    versions = sorted(files.keys(), key=lambda v: tuple(map(int, v.split("."))), reverse=True)
    return versions[0] if versions else None


def main():
    parser = argparse.ArgumentParser(description="Oppm Command Line Interface")
    subparsers = parser.add_subparsers(dest="command")

    # install <package>
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Name of the package to install")

    args = parser.parse_args()

    if args.command == "install":
        pkg = args.package.lower()
        print(f"Installing {pkg}...")

        manifest_url = f"{BASE_URL}/{pkg}/manifest.json"
        manifest = GetManifest(manifest_url)

        if not manifest:
            print("Failed: manifest not found.")
            exit(1)

        files = manifest.get("files", {})
        if not files:
            print("Manifest has no files.")
            exit(1)

        latest_version = pick_latest_version(files)
        if not latest_version:
            print("Couldn’t determine latest version.")
            exit(1)

        filename = files[latest_version]
        file_url = f"{BASE_URL}/{pkg}/{filename}"

        dest_path = os.path.join(INSTALL_DIR, pkg, filename)
        DownloadFile(file_url, dest_path)

        print(f"✅ Installed {pkg} v{latest_version}")


if __name__ == "__main__":
    main()
