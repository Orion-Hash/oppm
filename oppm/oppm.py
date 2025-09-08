#!/usr/bin/env python3
"""
OPPM - Orion Package Manager
A local package manager that works like pip but pulls from GitHub
"""

import os
import sys
import json
import shutil
import zipfile
import argparse
import tempfile
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from typing import Dict, List, Optional, Set
import hashlib

class OPPM:
    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/Orion-Hash/oppm/main/packages"
        self.api_url = "https://api.github.com/repos/Orion-Hash/oppm/contents/packages"
        self.local_packages_dir = Path.home() / ".oppm" / "packages"
        self.installed_packages_file = Path.home() / ".oppm" / "installed.json"
        self.cache_dir = Path.home() / ".oppm" / "cache"
        
        # Create directories if they don't exist
        self.local_packages_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load installed packages
        self.installed_packages = self._load_installed_packages()
    
    def _load_installed_packages(self) -> Dict:
        """Load the list of installed packages"""
        if self.installed_packages_file.exists():
            try:
                with open(self.installed_packages_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_installed_packages(self):
        """Save the list of installed packages"""
        self.installed_packages_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.installed_packages_file, 'w') as f:
            json.dump(self.installed_packages, f, indent=2)
    
    def _fetch_url(self, url: str) -> bytes:
        """Fetch content from URL with error handling"""
        try:
            req = Request(url)
            req.add_header('User-Agent', 'OPPM/1.0')
            with urlopen(req) as response:
                return response.read()
        except (URLError, HTTPError) as e:
            raise Exception(f"Failed to fetch {url}: {e}")
    
    def _get_available_packages(self) -> List[str]:
        """Get list of available packages from GitHub API"""
        try:
            response = self._fetch_url(self.api_url)
            data = json.loads(response.decode())
            return [item['name'] for item in data if item['type'] == 'dir']
        except Exception as e:
            print(f"Warning: Could not fetch package list: {e}")
            return []
    
    def _get_package_info(self, package_name: str) -> Dict:
        """Get package information from package.json"""
        url = f"{self.base_url}/{package_name}/package.json"
        try:
            response = self._fetch_url(url)
            return json.loads(response.decode())
        except Exception as e:
            raise Exception(f"Package '{package_name}' not found or invalid: {e}")
    
    def _download_package_files(self, package_name: str, package_info: Dict, temp_dir: Path):
        """Download all package files to temporary directory"""
        files = package_info.get('files', [])
        if not files:
            raise Exception(f"No files specified in package '{package_name}'")
        
        for file_path in files:
            url = f"{self.base_url}/{package_name}/{file_path}"
            try:
                content = self._fetch_url(url)
                file_dest = temp_dir / file_path
                file_dest.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_dest, 'wb') as f:
                    f.write(content)
                
                print(f"  Downloaded: {file_path}")
            except Exception as e:
                raise Exception(f"Failed to download {file_path}: {e}")
    
    def _resolve_dependencies(self, package_name: str, resolved: Set[str] = None) -> List[str]: # Type: ignore
        """Recursively resolve package dependencies"""
        if resolved is None:
            resolved = set()
        
        if package_name in resolved:
            return []
        
        resolved.add(package_name)
        dependencies = []
        
        try:
            package_info = self._get_package_info(package_name)
            deps = package_info.get('dependencies', [])
            
            for dep in deps:
                if dep not in self.installed_packages:
                    dependencies.extend(self._resolve_dependencies(dep, resolved))
                    dependencies.append(dep)
        except Exception as e:
            print(f"Warning: Could not resolve dependencies for {package_name}: {e}")
        
        return dependencies
    
    def install(self, package_name: str, force: bool = False):
        """Install a package and its dependencies"""
        if package_name in self.installed_packages and not force:
            print(f"Package '{package_name}' is already installed. Use --force to reinstall.")
            return
        
        print(f"Installing package: {package_name}")
        
        # Get package info
        try:
            package_info = self._get_package_info(package_name)
        except Exception as e:
            print(f"Error: {e}")
            return
        
        # Resolve and install dependencies first
        dependencies = self._resolve_dependencies(package_name)
        for dep in dependencies:
            if dep != package_name:
                print(f"Installing dependency: {dep}")
                self.install(dep, force=False)
        
        # Create package directory
        package_dir = self.local_packages_dir / package_name
        if package_dir.exists() and not force:
            print(f"Package directory already exists: {package_dir}")
            return
        
        # Download package files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            try:
                self._download_package_files(package_name, package_info, temp_path)
                
                # Remove existing directory if force install
                if package_dir.exists():
                    shutil.rmtree(package_dir)
                
                # Copy files to package directory
                shutil.copytree(temp_path, package_dir)
                
                # Run post-install script if it exists
                post_install_script = package_dir / "post_install.py"
                if post_install_script.exists():
                    print("  Running post-install script...")
                    try:
                        subprocess.run([sys.executable, str(post_install_script)], 
                                     cwd=package_dir, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"  Warning: Post-install script failed: {e}")
                
                # Mark as installed
                self.installed_packages[package_name] = {
                    'version': package_info.get('version', '1.0.0'),
                    'description': package_info.get('description', ''),
                    'installed_files': package_info.get('files', []),
                    'dependencies': package_info.get('dependencies', [])
                }
                self._save_installed_packages()
                
                print(f"Successfully installed: {package_name}")
                
            except Exception as e:
                print(f"Error installing package: {e}")
                if package_dir.exists():
                    shutil.rmtree(package_dir)
    
    def uninstall(self, package_name: str):
        """Uninstall a package"""
        if package_name not in self.installed_packages:
            print(f"Package '{package_name}' is not installed.")
            return
        
        # Check if other packages depend on this one
        dependents = []
        for pkg, info in self.installed_packages.items():
            if package_name in info.get('dependencies', []):
                dependents.append(pkg)
        
        if dependents:
            print(f"Cannot uninstall '{package_name}' because it's required by: {', '.join(dependents)}")
            print("Uninstall the dependent packages first, or use --force")
            return
        
        package_dir = self.local_packages_dir / package_name
        
        # Run pre-uninstall script if it exists
        pre_uninstall_script = package_dir / "pre_uninstall.py"
        if pre_uninstall_script.exists():
            print("Running pre-uninstall script...")
            try:
                subprocess.run([sys.executable, str(pre_uninstall_script)], 
                             cwd=package_dir, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Warning: Pre-uninstall script failed: {e}")
        
        # Remove package directory
        if package_dir.exists():
            shutil.rmtree(package_dir)
        
        # Remove from installed packages
        del self.installed_packages[package_name]
        self._save_installed_packages()
        
        print(f"Successfully uninstalled: {package_name}")
    
    def list_installed(self):
        """List all installed packages"""
        if not self.installed_packages:
            print("No packages installed.")
            return
        
        print("Installed packages:")
        for name, info in self.installed_packages.items():
            version = info.get('version', 'unknown')
            description = info.get('description', 'No description')
            print(f"  {name} ({version}): {description}")
    
    def list_available(self):
        """List all available packages"""
        print("Fetching available packages...")
        packages = self._get_available_packages()
        
        if not packages:
            print("No packages available or could not fetch package list.")
            return
        
        print("Available packages:")
        for package in packages:
            installed = "✓" if package in self.installed_packages else " "
            try:
                info = self._get_package_info(package)
                description = info.get('description', 'No description')
                version = info.get('version', 'unknown')
                print(f"  [{installed}] {package} ({version}): {description}")
            except:
                print(f"  [{installed}] {package}: Unable to fetch info")
    
    def show_package_info(self, package_name: str):
        """Show detailed information about a package"""
        try:
            info = self._get_package_info(package_name)
            installed = package_name in self.installed_packages
            
            print(f"Package: {package_name}")
            print(f"Version: {info.get('version', 'unknown')}")
            print(f"Description: {info.get('description', 'No description')}")
            print(f"Author: {info.get('author', 'Unknown')}")
            print(f"Installed: {'Yes' if installed else 'No'}")
            
            dependencies = info.get('dependencies', [])
            if dependencies:
                print(f"Dependencies: {', '.join(dependencies)}")
            
            files = info.get('files', [])
            if files:
                print(f"Files ({len(files)}):")
                for file_path in files:
                    print(f"  - {file_path}")
                    
        except Exception as e:
            print(f"Error: {e}")
    
    def update(self, package_name: str = None): # type: ignore
        """Update a specific package or all packages"""
        if package_name:
            if package_name not in self.installed_packages:
                print(f"Package '{package_name}' is not installed.")
                return
            print(f"Updating {package_name}...")
            self.install(package_name, force=True)
        else:
            print("Updating all installed packages...")
            for pkg in list(self.installed_packages.keys()):
                print(f"Updating {pkg}...")
                self.install(pkg, force=True)


def main():
    parser = argparse.ArgumentParser(description="OPPM - Orion Package Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name to install')
    install_parser.add_argument('--force', action='store_true', help='Force reinstall')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name to uninstall')
    
    # List commands
    subparsers.add_parser('list', help='List installed packages')
    subparsers.add_parser('search', help='List available packages')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show package information')
    show_parser.add_argument('package', help='Package name to show')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update packages')
    update_parser.add_argument('package', nargs='?', help='Package name to update (all if not specified)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    oppm = OPPM()
    
    try:
        if args.command == 'install':
            oppm.install(args.package, args.force)
        elif args.command == 'uninstall':
            oppm.uninstall(args.package)
        elif args.command == 'list':
            oppm.list_installed()
        elif args.command == 'search':
            oppm.list_available()
        elif args.command == 'show':
            oppm.show_package_info(args.package)
        elif args.command == 'update':
            oppm.update(args.package)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()