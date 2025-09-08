#!/usr/bin/env python3
"""
OPPM Package.json Creator GUI
A graphical interface for creating package.json files for OPPM packages
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

class PackageJsonCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OPPM Package.json Creator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Package data
        self.package_data = {
            "name": "",
            "version": "1.0.0",
            "description": "",
            "author": "",
            "files": [],
            "dependencies": [],
            "keywords": [],
            "license": "MIT",
            "homepage": "",
            "repository": ""
        }
        
        # Current working directory for file selection
        self.current_directory = os.getcwd()
        
        self.setup_ui()
        self.setup_validation()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Basic Info Tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Info")
        self.setup_basic_info_tab(basic_frame)
        
        # Files Tab
        files_frame = ttk.Frame(notebook)
        notebook.add(files_frame, text="Files")
        self.setup_files_tab(files_frame)
        
        # Dependencies Tab
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="Dependencies")
        self.setup_dependencies_tab(deps_frame)
        
        # Advanced Tab
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Advanced")
        self.setup_advanced_tab(advanced_frame)
        
        # Preview Tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="Preview")
        self.setup_preview_tab(preview_frame)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="Load from Directory", 
                  command=self.load_from_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="Load Existing", 
                  command=self.load_existing).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Validate", 
                  command=self.validate_package).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Save", 
                  command=self.save_package_json).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.RIGHT, padx=5)
    
    def setup_basic_info_tab(self, parent):
        """Setup basic package information tab"""
        # Package Name
        ttk.Label(parent, text="Package Name*:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(parent, textvariable=self.name_var, width=50)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        self.name_entry.bind('<KeyRelease>', self.validate_package_name)
        
        # Version
        ttk.Label(parent, text="Version*:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.version_var = tk.StringVar(value="1.0.0")
        self.version_entry = ttk.Entry(parent, textvariable=self.version_var, width=20)
        self.version_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        self.version_entry.bind('<KeyRelease>', self.validate_version)
        
        # Description
        ttk.Label(parent, text="Description*:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.description_text = scrolledtext.ScrolledText(parent, height=3, width=50)
        self.description_text.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Author
        ttk.Label(parent, text="Author:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.author_var = tk.StringVar()
        self.author_entry = ttk.Entry(parent, textvariable=self.author_var, width=50)
        self.author_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # License
        ttk.Label(parent, text="License:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.license_var = tk.StringVar(value="MIT")
        license_combo = ttk.Combobox(parent, textvariable=self.license_var, width=20,
                                   values=["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC", "Unlicense"])
        license_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Validation labels
        self.name_validation_label = ttk.Label(parent, text="", foreground="red")
        self.name_validation_label.grid(row=0, column=2, sticky=tk.W, padx=10)
        
        self.version_validation_label = ttk.Label(parent, text="", foreground="red")
        self.version_validation_label.grid(row=1, column=2, sticky=tk.W, padx=10)
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
    
    def setup_files_tab(self, parent):
        """Setup files selection tab"""
        # Instructions
        instructions = ttk.Label(parent, text="Select files to include in your package:")
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Frame for file operations
        file_ops_frame = ttk.Frame(parent)
        file_ops_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(file_ops_frame, text="Add File", 
                  command=self.add_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_ops_frame, text="Add Directory", 
                  command=self.add_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Auto-detect Python Files", 
                  command=self.auto_detect_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_ops_frame, text="Remove Selected", 
                  command=self.remove_selected_files).pack(side=tk.RIGHT)
        
        # File list
        files_frame = ttk.Frame(parent)
        files_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable listbox for files
        files_scroll_frame = ttk.Frame(files_frame)
        files_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        self.files_listbox = tk.Listbox(files_scroll_frame, selectmode=tk.EXTENDED)
        files_scrollbar = ttk.Scrollbar(files_scroll_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_dependencies_tab(self, parent):
        """Setup dependencies tab"""
        # Instructions
        instructions = ttk.Label(parent, text="Specify package dependencies (other OPPM packages):")
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # Add dependency frame
        add_dep_frame = ttk.Frame(parent)
        add_dep_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_dep_frame, text="Dependency Name:").pack(side=tk.LEFT)
        self.dep_entry_var = tk.StringVar()
        self.dep_entry = ttk.Entry(add_dep_frame, textvariable=self.dep_entry_var, width=30)
        self.dep_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.dep_entry.bind('<Return>', self.add_dependency)
        
        ttk.Button(add_dep_frame, text="Add", command=self.add_dependency).pack(side=tk.LEFT)
        ttk.Button(add_dep_frame, text="Remove Selected", 
                  command=self.remove_selected_dependencies).pack(side=tk.RIGHT)
        
        # Dependencies list
        deps_frame = ttk.Frame(parent)
        deps_frame.pack(fill=tk.BOTH, expand=True)
        
        self.deps_listbox = tk.Listbox(deps_frame, selectmode=tk.EXTENDED)
        deps_scrollbar = ttk.Scrollbar(deps_frame, orient=tk.VERTICAL, command=self.deps_listbox.yview)
        self.deps_listbox.configure(yscrollcommand=deps_scrollbar.set)
        
        self.deps_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        deps_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_advanced_tab(self, parent):
        """Setup advanced options tab"""
        # Keywords
        ttk.Label(parent, text="Keywords (comma-separated):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.keywords_var = tk.StringVar()
        self.keywords_entry = ttk.Entry(parent, textvariable=self.keywords_var, width=50)
        self.keywords_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Homepage
        ttk.Label(parent, text="Homepage URL:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.homepage_var = tk.StringVar()
        self.homepage_entry = ttk.Entry(parent, textvariable=self.homepage_var, width=50)
        self.homepage_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Repository
        ttk.Label(parent, text="Repository URL:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.repository_var = tk.StringVar()
        self.repository_entry = ttk.Entry(parent, textvariable=self.repository_var, width=50)
        self.repository_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Custom fields
        ttk.Label(parent, text="Custom JSON:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        self.custom_json_text = scrolledtext.ScrolledText(parent, height=10, width=50)
        self.custom_json_text.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=(10, 0))
        
        # Instructions for custom JSON
        instructions = ttk.Label(parent, text="Add custom fields as valid JSON (will be merged with package.json):",
                               font=("TkDefaultFont", 8))
        instructions.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        parent.columnconfigure(1, weight=1)
    
    def setup_preview_tab(self, parent):
        """Setup preview tab"""
        # Preview text area
        self.preview_text = scrolledtext.ScrolledText(parent, height=30, width=80)
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Update preview button
        ttk.Button(parent, text="Update Preview", 
                  command=self.update_preview).pack(side=tk.RIGHT)
    
    def setup_validation(self):
        """Setup validation for form fields"""
        # Bind validation events
        self.name_var.trace('w', self.on_field_change)
        self.version_var.trace('w', self.on_field_change)
        self.author_var.trace('w', self.on_field_change)
        self.license_var.trace('w', self.on_field_change)
        self.keywords_var.trace('w', self.on_field_change)
        self.homepage_var.trace('w', self.on_field_change)
        self.repository_var.trace('w', self.on_field_change)
    
    def on_field_change(self, *args):
        """Called when any field changes"""
        self.update_package_data()
    
    def validate_package_name(self, event=None):
        """Validate package name"""
        name = self.name_var.get()
        if not name:
            self.name_validation_label.config(text="Required field")
        elif not re.match(r'^[a-z0-9_-]+$', name):
            self.name_validation_label.config(text="Only lowercase letters, numbers, hyphens, and underscores allowed")
        else:
            self.name_validation_label.config(text="✓", foreground="green")
    
    def validate_version(self, event=None):
        """Validate version number"""
        version = self.version_var.get()
        if not version:
            self.version_validation_label.config(text="Required field")
        elif not re.match(r'^\d+\.\d+\.\d+', version):
            self.version_validation_label.config(text="Use semantic versioning (e.g., 1.0.0)")
        else:
            self.version_validation_label.config(text="✓", foreground="green")
    
    def update_package_data(self):
        """Update package data from form fields"""
        self.package_data.update({
            "name": self.name_var.get(),
            "version": self.version_var.get(),
            "description": self.description_text.get("1.0", tk.END).strip(),
            "author": self.author_var.get(),
            "license": self.license_var.get(),
            "keywords": [k.strip() for k in self.keywords_var.get().split(",") if k.strip()],
            "homepage": self.homepage_var.get(),
            "repository": self.repository_var.get()
        })
    
    def add_file(self):
        """Add individual file to package"""
        filetypes = [
            ("Python files", "*.py"),
            ("Text files", "*.txt"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(
            title="Select files to include",
            initialdir=self.current_directory,
            filetypes=filetypes
        )
        
        for file_path in files:
            rel_path = os.path.relpath(file_path, self.current_directory)
            if rel_path not in self.package_data["files"]:
                self.package_data["files"].append(rel_path)
                self.files_listbox.insert(tk.END, rel_path)
    
    def add_directory(self):
        """Add entire directory to package"""
        directory = filedialog.askdirectory(
            title="Select directory to include",
            initialdir=self.current_directory
        )
        
        if directory:
            for root, dirs, files in os.walk(directory):
                # Skip hidden directories and common exclude patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if not file.startswith('.') and not file.endswith('.pyc'):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, self.current_directory)
                        if rel_path not in self.package_data["files"]:
                            self.package_data["files"].append(rel_path)
                            self.files_listbox.insert(tk.END, rel_path)
    
    def auto_detect_files(self):
        """Auto-detect Python files in current directory"""
        python_files = []
        for root, dirs, files in os.walk(self.current_directory):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.current_directory)
                    if rel_path not in self.package_data["files"]:
                        python_files.append(rel_path)
        
        if python_files:
            for file_path in python_files:
                self.package_data["files"].append(file_path)
                self.files_listbox.insert(tk.END, file_path)
            messagebox.showinfo("Files Added", f"Added {len(python_files)} Python files")
        else:
            messagebox.showinfo("No Files", "No Python files found in current directory")
    
    def remove_selected_files(self):
        """Remove selected files from list"""
        selected_indices = self.files_listbox.curselection()
        for index in reversed(selected_indices):
            file_path = self.files_listbox.get(index)
            self.package_data["files"].remove(file_path)
            self.files_listbox.delete(index)
    
    def add_dependency(self, event=None):
        """Add dependency to list"""
        dep_name = self.dep_entry_var.get().strip()
        if dep_name and dep_name not in self.package_data["dependencies"]:
            self.package_data["dependencies"].append(dep_name)
            self.deps_listbox.insert(tk.END, dep_name)
            self.dep_entry_var.set("")
    
    def remove_selected_dependencies(self):
        """Remove selected dependencies"""
        selected_indices = self.deps_listbox.curselection()
        for index in reversed(selected_indices):
            dep_name = self.deps_listbox.get(index)
            self.package_data["dependencies"].remove(dep_name)
            self.deps_listbox.delete(index)
    
    def load_from_directory(self):
        """Load package info from directory structure"""
        directory = filedialog.askdirectory(title="Select package directory")
        if directory:
            self.current_directory = directory
            
            # Try to guess package name from directory name
            package_name = os.path.basename(directory).lower().replace(" ", "_")
            self.name_var.set(package_name)
            
            # Auto-detect files
            self.auto_detect_files()
            
            messagebox.showinfo("Directory Loaded", f"Loaded from: {directory}")
    
    def load_existing(self):
        """Load existing package.json file"""
        file_path = filedialog.askopenfilename(
            title="Select package.json file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Update form fields
                self.name_var.set(data.get("name", ""))
                self.version_var.set(data.get("version", "1.0.0"))
                self.description_text.delete("1.0", tk.END)
                self.description_text.insert("1.0", data.get("description", ""))
                self.author_var.set(data.get("author", ""))
                self.license_var.set(data.get("license", "MIT"))
                self.keywords_var.set(", ".join(data.get("keywords", [])))
                self.homepage_var.set(data.get("homepage", ""))
                self.repository_var.set(data.get("repository", ""))
                
                # Update files list
                self.files_listbox.delete(0, tk.END)
                self.package_data["files"] = data.get("files", [])
                for file_path in self.package_data["files"]:
                    self.files_listbox.insert(tk.END, file_path)
                
                # Update dependencies list
                self.deps_listbox.delete(0, tk.END)
                self.package_data["dependencies"] = data.get("dependencies", [])
                for dep in self.package_data["dependencies"]:
                    self.deps_listbox.insert(tk.END, dep)
                
                # Set current directory to the file's directory
                self.current_directory = os.path.dirname(file_path)
                
                messagebox.showinfo("File Loaded", "Package.json loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def validate_package(self):
        """Validate the current package configuration"""
        self.update_package_data()
        errors = []
        warnings = []
        
        # Required fields
        if not self.package_data["name"]:
            errors.append("Package name is required")
        elif not re.match(r'^[a-z0-9_-]+$', self.package_data["name"]):
            errors.append("Package name can only contain lowercase letters, numbers, hyphens, and underscores")
        
        if not self.package_data["version"]:
            errors.append("Version is required")
        elif not re.match(r'^\d+\.\d+\.\d+', self.package_data["version"]):
            errors.append("Version should follow semantic versioning (e.g., 1.0.0)")
        
        if not self.package_data["description"]:
            errors.append("Description is required")
        
        if not self.package_data["files"]:
            errors.append("At least one file must be included")
        
        # Warnings
        if not self.package_data["author"]:
            warnings.append("Author field is empty")
        
        if len(self.package_data["description"]) < 10:
            warnings.append("Description is very short")
        
        # Check if files exist
        missing_files = []
        for file_path in self.package_data["files"]:
            full_path = os.path.join(self.current_directory, file_path)
            if not os.path.exists(full_path):
                missing_files.append(file_path)
        
        if missing_files:
            errors.append(f"Missing files: {', '.join(missing_files)}")
        
        # Show results
        if errors:
            messagebox.showerror("Validation Errors", "\n".join([f"• {error}" for error in errors]))
        elif warnings:
            result = messagebox.askokcancel("Validation Warnings", 
                                          "Warnings found:\n" + "\n".join([f"• {warning}" for warning in warnings]) +
                                          "\n\nContinue anyway?")
            if result:
                messagebox.showinfo("Validation", "Package validation completed with warnings")
        else:
            messagebox.showinfo("Validation", "Package validation passed successfully!")
    
    def update_preview(self):
        """Update the JSON preview"""
        self.update_package_data()
        
        # Create clean package data (remove empty fields)
        clean_data = {}
        for key, value in self.package_data.items():
            if value:  # Only include non-empty values
                clean_data[key] = value
        
        # Try to merge custom JSON
        try:
            custom_json = self.custom_json_text.get("1.0", tk.END).strip()
            if custom_json:
                custom_data = json.loads(custom_json)
                clean_data.update(custom_data)
        except json.JSONDecodeError:
            pass  # Ignore invalid custom JSON for preview
        
        # Format and display JSON
        try:
            json_str = json.dumps(clean_data, indent=2, sort_keys=True)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", json_str)
        except Exception as e:
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", f"Error generating preview: {str(e)}")
    
    def save_package_json(self):
        """Save package.json file"""
        if not self.validate_package():
            return
        
        self.update_package_data()
        
        # Create clean package data
        clean_data = {}
        for key, value in self.package_data.items():
            if value:  # Only include non-empty values
                clean_data[key] = value
        
        # Try to merge custom JSON
        try:
            custom_json = self.custom_json_text.get("1.0", tk.END).strip()
            if custom_json:
                custom_data = json.loads(custom_json)
                clean_data.update(custom_data)
        except json.JSONDecodeError as e:
            messagebox.showerror("Custom JSON Error", f"Invalid custom JSON: {str(e)}")
            return
        
        # Ask where to save
        file_path = filedialog.asksaveasfilename(
            title="Save package.json",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.current_directory,
            initialfilename="package.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(clean_data, f, indent=2, sort_keys=True)
                messagebox.showinfo("Success", f"Package.json saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def clear_all(self):
        """Clear all form fields"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all fields?"):
            # Reset all form fields
            self.name_var.set("")
            self.version_var.set("1.0.0")
            self.description_text.delete("1.0", tk.END)
            self.author_var.set("")
            self.license_var.set("MIT")
            self.keywords_var.set("")
            self.homepage_var.set("")
            self.repository_var.set("")
            self.custom_json_text.delete("1.0", tk.END)
            
            # Clear lists
            self.files_listbox.delete(0, tk.END)
            self.deps_listbox.delete(0, tk.END)
            
            # Reset package data
            self.package_data = {
                "name": "",
                "version": "1.0.0",
                "description": "",
                "author": "",
                "files": [],
                "dependencies": [],
                "keywords": [],
                "license": "MIT",
                "homepage": "",
                "repository": ""
            }


def main():
    root = tk.Tk()
    app = PackageJsonCreatorGUI(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap("package.ico")
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()