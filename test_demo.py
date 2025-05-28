#!/usr/bin/env python3
"""
Demo script to test the Missing File Scanner functionality
This script creates a test directory structure and demonstrates the scanning logic
"""

import os
import tempfile
import shutil
from pathlib import Path

def create_test_structure():
    """Create a test directory structure for demonstration"""
    # Create temporary directory
    test_dir = tempfile.mkdtemp(prefix="missing_file_test_")
    print(f"Created test directory: {test_dir}")
    
    # Create subdirectories
    subdirs = [
        "folder1",
        "folder2", 
        "folder3/subfolder1",
        "folder3/subfolder2",
        "folder4",
        "empty_folder"
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(test_dir, subdir), exist_ok=True)
    
    # Create test files (some folders will have the target file, others won't)
    test_files = {
        "folder1": ["config.txt", "readme.md"],
        "folder2": ["data.csv", "config.txt"],
        "folder3": ["config.txt"],
        "folder3/subfolder1": ["config.txt", "other.txt"],
        "folder3/subfolder2": ["different.txt"],  # Missing config.txt
        "folder4": ["readme.md"],  # Missing config.txt
        # empty_folder has no files
    }
    
    for folder, files in test_files.items():
        folder_path = os.path.join(test_dir, folder)
        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, 'w') as f:
                f.write(f"This is {file} in {folder}")
    
    return test_dir

def scan_for_missing_file(root_folder, target_filename):
    """
    Simulate the scanning logic from the main application
    Returns list of folders where the target file is missing
    """
    missing_folders = []
    
    # Get all directories
    for root, dirs, files in os.walk(root_folder):
        # Check if target file exists in this directory
        file_found = False
        
        if '.' in target_filename:
            # Filename has extension, check exact match
            file_found = target_filename in files
        else:
            # Filename without extension, check for any file with that base name
            for file in files:
                name_without_ext = os.path.splitext(file)[0]
                if name_without_ext.lower() == target_filename.lower():
                    file_found = True
                    break
        
        if not file_found:
            missing_folders.append(root)
    
    return missing_folders

def main():
    """Run the demonstration"""
    print("=== Missing File Scanner Demo ===\n")
    
    # Create test structure
    test_dir = create_test_structure()
    
    try:
        print("\nTest directory structure created:")
        for root, dirs, files in os.walk(test_dir):
            level = root.replace(test_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        print(f"\n=== Scanning for 'config.txt' ===")
        missing_folders = scan_for_missing_file(test_dir, "config.txt")
        
        print(f"\nFolders missing 'config.txt':")
        if missing_folders:
            for folder in missing_folders:
                rel_path = os.path.relpath(folder, test_dir)
                if rel_path == '.':
                    rel_path = '(root)'
                print(f"  - {rel_path}")
        else:
            print("  None! File found in all folders.")
        
        print(f"\n=== Scanning for 'readme' (without extension) ===")
        missing_folders = scan_for_missing_file(test_dir, "readme")
        
        print(f"\nFolders missing 'readme' files:")
        if missing_folders:
            for folder in missing_folders:
                rel_path = os.path.relpath(folder, test_dir)
                if rel_path == '.':
                    rel_path = '(root)'
                print(f"  - {rel_path}")
        else:
            print("  None! File found in all folders.")
            
        print(f"\n=== Demo completed successfully! ===")
        print(f"\nTo run the GUI application, use:")
        print(f"  python missing_file_scanner.py")
        
    finally:
        # Clean up
        print(f"\nCleaning up test directory: {test_dir}")
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    main() 