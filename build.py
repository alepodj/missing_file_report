"""
Build script for Missing File Scanner
Creates a standalone executable using PyInstaller
Cross-platform support for Windows, Linux, and macOS
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def get_platform_info():
    """Get platform-specific information"""
    system = platform.system().lower()
    
    if system == "windows":
        return {
            "name": "Windows",
            "exe_extension": ".exe",
            "data_separator": ";",
            "script_extension": ".bat",
            "script_template": """@echo off
echo Starting Missing File Scanner...
MissingFileScanner{exe_ext}
pause
""",
            "icon": "📊"
        }
    elif system == "darwin":  # macOS
        return {
            "name": "macOS",
            "exe_extension": "",
            "data_separator": ":",
            "script_extension": ".command",
            "script_template": """#!/bin/bash
echo "Starting Missing File Scanner..."
./MissingFileScanner{exe_ext}
read -p "Press any key to continue..."
""",
            "icon": "🍎"
        }
    else:  # Linux and other Unix-like systems
        return {
            "name": "Linux",
            "exe_extension": "",
            "data_separator": ":",
            "script_extension": ".sh",
            "script_template": """#!/bin/bash
echo "Starting Missing File Scanner..."
./MissingFileScanner{exe_ext}
read -p "Press any key to continue..."
""",
            "icon": "🐧"
        }

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
    platform_info = get_platform_info()
    print(f"🔨 Building executable for {platform_info['name']} {platform_info['icon']}...")
    
    # PyInstaller command with options
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Create a single executable file
        "--windowed",                   # Hide console window (GUI app)
        "--name=MissingFileScanner",    # Name of the executable
        "--icon=NONE",                  # No icon (can be added later)
        f"--add-data=requirements.txt{platform_info['data_separator']}.", # Include requirements.txt with correct separator
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
            exe_name = f"MissingFileScanner{platform_info['exe_extension']}"
            exe_path = Path("dist") / exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable location: {exe_path.absolute()}")
                print(f"📏 File size: {size_mb:.1f} MB")
                return True
            else:
                print(f"❌ Executable not found in expected location: {exe_path}")
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
    platform_info = get_platform_info()
    print(f"📦 Creating portable package for {platform_info['name']}...")
    
    package_dir = Path("MissingFileScanner_Portable")
    
    # Create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy executable
    exe_name = f"MissingFileScanner{platform_info['exe_extension']}"
    exe_source = Path("dist") / exe_name
    if exe_source.exists():
        shutil.copy2(exe_source, package_dir / exe_name)
        print(f"✅ Copied executable: {exe_name}")
        
        # Make executable on Unix-like systems
        if platform_info['exe_extension'] == "":
            os.chmod(package_dir / exe_name, 0o755)
            print("✅ Set executable permissions")
    
    # Copy documentation
    files_to_copy = ["README.md", "requirements.txt"]
    for file_name in files_to_copy:
        if Path(file_name).exists():
            shutil.copy2(file_name, package_dir / file_name)
            print(f"✅ Copied {file_name}")
    
    # Create platform-specific launcher script
    script_name = f"Run_Scanner{platform_info['script_extension']}"
    script_content = platform_info['script_template'].format(exe_ext=platform_info['exe_extension'])
    
    script_path = package_dir / script_name
    with open(script_path, "w", newline='\n') as f:
        f.write(script_content)
    
    # Make script executable on Unix-like systems
    if platform_info['script_extension'] in ['.sh', '.command']:
        os.chmod(script_path, 0o755)
        print(f"✅ Created executable launcher script: {script_name}")
    else:
        print(f"✅ Created launcher script: {script_name}")
    
    print(f"📦 Portable package created: {package_dir.absolute()}")

def main():
    """Main build process"""
    platform_info = get_platform_info()
    
    print(f"🚀 Missing File Scanner - Build Script")
    print(f"{platform_info['icon']} Building for {platform_info['name']}")
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
    
    exe_name = f"MissingFileScanner{platform_info['exe_extension']}"
    script_name = f"Run_Scanner{platform_info['script_extension']}"
    
    print("\n" + "=" * 50)
    print("🎉 Build completed successfully!")
    print(f"\nFiles created for {platform_info['name']}:")
    print(f"  📁 dist/{exe_name} - Standalone executable")
    print(f"  📁 MissingFileScanner_Portable/ - Portable package")
    print(f"  📄 MissingFileScanner_Portable/{script_name} - Launcher script")
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