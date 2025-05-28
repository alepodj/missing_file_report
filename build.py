#!/usr/bin/env python3
"""
Build script for Missing File Scanner
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
        return True
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)

def create_executable():
    """Create the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    # PyInstaller command with options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # Hide console window (GUI app)
        "--name=MissingFileScanner",    # Name of the executable
        "--icon=NONE",                  # No icon (can be added later)
        "--add-data=requirements.txt;.", # Include requirements.txt
        "--distpath=dist",              # Output directory
        "--workpath=build",             # Build directory
        "--specpath=.",                 # Spec file location
        "missing_file_scanner.py"       # Main script
    ]
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Executable created successfully!")
            
            # Check if executable exists
            exe_path = Path("dist/MissingFileScanner.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable location: {exe_path.absolute()}")
                print(f"📏 File size: {size_mb:.1f} MB")
                return True
            else:
                print("❌ Executable not found in expected location")
                return False
        else:
            print("❌ PyInstaller failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running PyInstaller: {e}")
        return False

def create_portable_package():
    """Create a portable package with the executable and documentation"""
    print("📦 Creating portable package...")
    
    package_dir = Path("MissingFileScanner_Portable")
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable
    exe_source = Path("dist/MissingFileScanner.exe")
    if exe_source.exists():
        shutil.copy2(exe_source, package_dir / "MissingFileScanner.exe")
        print("✅ Copied executable")
    
    # Copy documentation
    files_to_copy = ["README.md", "requirements.txt"]
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, package_dir / file_name)
            print(f"✅ Copied {file_name}")
    
    # Create a simple batch file for easy running
    batch_content = """@echo off
echo Starting Missing File Scanner...
MissingFileScanner.exe
pause
"""
    with open(package_dir / "Run_Scanner.bat", "w") as f:
        f.write(batch_content)
    print("✅ Created Run_Scanner.bat")
    
    print(f"📦 Portable package created: {package_dir.absolute()}")

def main():
    """Main build process"""
    print("🚀 Missing File Scanner - Build Script")
    print("=" * 50)
    
    # Check if main script exists
    if not Path("missing_file_scanner.py").exists():
        print("❌ missing_file_scanner.py not found!")
        return False
    
    # Step 1: Check/Install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Create executable
    if not create_executable():
        return False
    
    # Step 4: Create portable package
    create_portable_package()
    
    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print("\nFiles created:")
    print("  📁 dist/MissingFileScanner.exe - Standalone executable")
    print("  📁 MissingFileScanner_Portable/ - Portable package")
    print("\nYou can now distribute the executable or the entire portable folder.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Build failed!")
        sys.exit(1)
    else:
        print("\n✅ Build successful!")
        sys.exit(0) 