# Missing File Scanner

A modern GUI application with Windows 11 styling that scans folders and subfolders to identify directories where a specific file is missing.

## Features

- **Modern Windows 11 UI**: Clean, modern interface with Windows 11-inspired design
- **Flexible File Search**: Search for files with full or partial matching, with or without extensions
- **Folder Exclusion**: Skip folders containing specific strings (e.g., temp, cache, .git)
- **Interactive Results**: Clickable folder paths with hover effects and context menus
- **Recursive Scanning**: Scans all folders and subfolders in the selected directory
- **Real-time Progress**: Live progress bar and status updates during scanning
- **Background Processing**: Non-blocking UI with threaded scanning
- **Detailed Results**: Lists all folders where the target file is missing
- **Portable Executable**: Build standalone .exe files for easy distribution

## Installation

### Option 1: Run from Source

1. **Install Python 3.8 or higher** (if not already installed)

2. **Install PySide6**:

   ```bash
   pip install -r requirements.txt
   ```

   Or install directly:

   ```bash
   pip install PySide6
   ```

### Option 2: Use Portable Executable

1. **Build the executable**:

   ```bash
   python build.py
   ```

2. **Use the portable package**: Find the executable in `MissingFileScanner_Portable/` folder

## Usage

### Running the Application

**From Source**:

```bash
python missing_file_scanner.py
```

**From Batch File**:
Double-click: `run_scanner.bat`

**From Executable**:
Double-click: `MissingFileScanner.exe` or `Run_Scanner.bat`

### Using the Interface

1. **Select Target Folder**: Click the folder input field or "Browse" button to choose the root folder to scan

2. **Enter File Name**: Type the filename you're looking for

   - **Exact match**: `document.pdf`, `config.txt`
   - **Partial match**: `config` (matches config.txt, config.json, myconfig.ini, etc.)
   - **Without extension**: `readme` (matches readme.md, readme.txt, etc.)

3. **Exclude Folders** (Optional): Enter comma-separated terms to skip folders containing those strings

   - Example: `temp, cache, .git, node_modules`
   - Skips any folder with these terms in the name or path

4. **Start Scan**: Click "🔍 Start Scan" to begin the process

5. **View Results**: Missing folders will be listed in the results area
   - **Hover**: Lines highlight in blue with pointing hand cursor
   - **Double-click**: Opens folder in Windows Explorer
   - **Right-click**: Context menu with "Open Folder" and "Copy Path" options
   - **Tooltip**: Shows "Double-click to open folder in Explorer"

## Building Executable

Create a standalone executable that doesn't require Python installation:

```bash
python build.py
```

This creates:

- `dist/MissingFileScanner.exe` - Standalone executable (42MB)
- `MissingFileScanner_Portable/` - Complete portable package with documentation

The build script automatically:

- Installs PyInstaller if needed
- Cleans previous builds
- Creates a windowed (no console) executable
- Bundles all dependencies
- Creates a portable distribution package

## Demo

To see the scanning functionality in action without the GUI, run the demo script:

```bash
python test_demo.py
```

This creates a temporary test directory structure and demonstrates how the application finds missing files.

## How It Works

The application performs the following steps:

1. **Folder Discovery**: Recursively finds all folders and subfolders in the target directory
2. **Exclusion Filtering**: Skips folders containing any exclusion terms (if specified)
3. **File Checking**: For each remaining folder, checks if the specified file exists:
   - **Exact full filename match** (with extension)
   - **Exact filename match** without extension
   - **Partial match** in full filename (with extension)
   - **Partial match** in filename without extension
4. **Results Collection**: Collects all folders where the file is NOT found
5. **Interactive Display**: Shows clickable results with folder navigation options

## Example Use Cases

- **Software Deployment**: Ensure configuration files exist in all application folders
- **Content Management**: Verify required files are present across multiple directories
- **Quality Assurance**: Check that documentation or readme files exist in project folders
- **Backup Verification**: Confirm important files are present in backup directories
- **Development**: Find missing files while excluding temporary/cache folders

## Technical Details

- **Framework**: PySide6 for modern GUI
- **Threading**: Background scanning to keep UI responsive
- **File System**: Uses Python's `os.walk()` for efficient directory traversal
- **Cursor Management**: Application-level cursor override for text widgets
- **Path Handling**: Normalized Windows path separators for compatibility
- **Build System**: PyInstaller for creating standalone executables

## Requirements

- Python 3.8+
- PySide6 6.9.0+
- Windows 10/11 (optimized for Windows 11 styling)

## Files Included

- `missing_file_scanner.py` - Main GUI application
- `build.py` - Build script for creating executables
- `test_demo.py` - Command-line demo script
- `run_scanner.bat` - Windows batch file to run the application
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Distribution

### For End Users

- Share the `MissingFileScanner_Portable/` folder
- No Python installation required
- Run `MissingFileScanner.exe` or `Run_Scanner.bat`

### For Developers

- Clone/download the source code
- Install requirements: `pip install -r requirements.txt`
- Run: `python missing_file_scanner.py`

## Troubleshooting

### Permission Errors

The application handles permission errors gracefully and will skip folders it cannot access.

### Build Issues

If the build fails:

1. Ensure Python and pip are properly installed
2. Try running: `pip install --upgrade pyinstaller`
3. Check that all source files are present

### Cursor Not Changing

The application uses application-level cursor override to ensure cursor changes work in text widgets.

## Screenshots

The application features:

- Clean, modern Windows 11-inspired interface
- Side-by-side input fields for space efficiency
- Intuitive folder browser integration
- Real-time progress tracking with percentage display
- Interactive results with hover effects and context menus
- Comprehensive exclusion filtering options

## License

This project is open source and available under the MIT License.
