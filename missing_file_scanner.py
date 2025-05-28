import sys
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QLineEdit, QTextEdit, QLabel, 
                             QFileDialog, QProgressBar, QFrame, QScrollArea, QMessageBox, QMenu)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QAction, QCursor


class FileScannerThread(QThread):
    """Background thread for scanning directories"""
    progress_updated = Signal(int, int)  # current, total
    folder_found = Signal(str)  # folder path where file is missing
    scan_completed = Signal(int)  # total missing count
    
    def __init__(self, root_folder, filename, exclusion_list=None):
        super().__init__()
        self.root_folder = root_folder
        self.filename = filename
        self.exclusion_list = exclusion_list or []
        self.missing_folders = []
        
    def should_exclude_folder(self, folder_path):
        """Check if folder should be excluded based on exclusion list"""
        if not self.exclusion_list:
            return False
            
        folder_name = os.path.basename(folder_path).lower()
        folder_path_lower = folder_path.lower()
        
        for exclusion_term in self.exclusion_list:
            exclusion_lower = exclusion_term.strip().lower()
            if not exclusion_lower:
                continue
                
            # Check if exclusion term is in folder name or full path
            if exclusion_lower in folder_name or exclusion_lower in folder_path_lower:
                return True
                
        return False
        
    def run(self):
        """Scan directories for missing files"""
        try:
            # Clear previous results
            self.missing_folders.clear()
            
            # Get all subdirectories (avoid duplicates)
            all_dirs = []
            for root, dirs, files in os.walk(self.root_folder):
                all_dirs.append(root)
                # Don't add subdirectories here as os.walk will visit them
            
            total_dirs = len(all_dirs)
            
            for i, folder_path in enumerate(all_dirs):
                # Check if folder should be excluded
                if self.should_exclude_folder(folder_path):
                    continue
                    
                # Check if file exists in this folder
                file_found = False
                
                try:
                    for file in os.listdir(folder_path):
                        if os.path.isfile(os.path.join(folder_path, file)):
                            # Get filename without extension for comparison
                            name_without_ext = os.path.splitext(file)[0]
                            
                            # Check multiple matching criteria
                            search_term = self.filename.lower()
                            file_lower = file.lower()
                            name_without_ext_lower = name_without_ext.lower()
                            
                            # 1. Exact full filename match (with extension)
                            if file_lower == search_term:
                                file_found = True
                                break
                            
                            # 2. Exact filename match without extension
                            if name_without_ext_lower == search_term:
                                file_found = True
                                break
                            
                            # 3. Partial match in full filename (with extension)
                            if search_term in file_lower:
                                file_found = True
                                break
                            
                            # 4. Partial match in filename without extension
                            if search_term in name_without_ext_lower:
                                file_found = True
                                break
                                
                except PermissionError:
                    # Skip folders we can't access
                    continue
                
                if not file_found:
                    # Normalize path separators for Windows
                    normalized_path = os.path.normpath(folder_path)
                    self.missing_folders.append(normalized_path)
                    self.folder_found.emit(normalized_path)
                
                self.progress_updated.emit(i + 1, total_dirs)
            
            self.scan_completed.emit(len(self.missing_folders))
            
        except Exception as e:
            print(f"Error during scan: {e}")


class ModernButton(QPushButton):
    """Custom button with modern Windows 11 styling"""
    def __init__(self, text, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f3f2f1;
                    color: #323130;
                    border: 1px solid #d2d0ce;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #edebe9;
                    border-color: #c7c6c4;
                }
                QPushButton:pressed {
                    background-color: #e1dfdd;
                }
            """)


class ModernLineEdit(QLineEdit):
    """Custom line edit with modern styling"""
    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(40)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e1dfdd;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                color: #323130;
            }
            QLineEdit:focus {
                border-color: #0078d4;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #c7c6c4;
            }
            QLineEdit::placeholder {
                color: #a19f9d;
                font-style: italic;
            }
        """)


class ClickableTextEdit(QTextEdit):
    """Custom QTextEdit that supports clickable folder paths and context menu"""
    
    def __init__(self):
        super().__init__()
        self.missing_folders = []
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setMouseTracking(True)  # Enable mouse tracking for hover effects
        self.current_hover_line = -1
        self.cursor_override_active = False  # Track cursor override state
        
    def add_folder_path(self, folder_path):
        """Add a folder path to the results and store it for context menu"""
        self.missing_folders.append(folder_path)
        self.append(folder_path)
        
    def clear_results(self):
        """Clear both the text and the stored folder paths"""
        self.clear()
        self.missing_folders.clear()
        self.current_hover_line = -1
        if self.cursor_override_active:
            QApplication.restoreOverrideCursor()
            self.cursor_override_active = False
        
    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        cursor = self.cursorForPosition(event.position().toPoint())
        cursor.select(cursor.SelectionType.LineUnderCursor)
        selected_line = cursor.selectedText().strip()
        
        # Get line number
        line_number = cursor.blockNumber()
        
        # Check if this line contains a valid folder path
        is_valid_path = False
        if selected_line:
            # Check exact match first
            if selected_line in self.missing_folders:
                is_valid_path = True
            else:
                # Check if any stored folder path matches this line
                for folder_path in self.missing_folders:
                    if folder_path.strip() == selected_line or selected_line in folder_path:
                        is_valid_path = True
                        break
        
        if is_valid_path:
            # Change cursor to pointing hand for clickable lines
            if not self.cursor_override_active:
                QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
                self.cursor_override_active = True
            self.setToolTip("Double-click to open folder in Explorer")
            
            # Highlight the line if it's different from current
            if line_number != self.current_hover_line:
                self.highlight_line(line_number)
                self.current_hover_line = line_number
        else:
            # Reset cursor and remove highlighting
            if self.cursor_override_active:
                QApplication.restoreOverrideCursor()
                self.cursor_override_active = False
            self.setToolTip("")
            if self.current_hover_line != -1:
                self.remove_highlighting()
                self.current_hover_line = -1
                
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        """Remove highlighting when mouse leaves the widget"""
        if self.cursor_override_active:
            QApplication.restoreOverrideCursor()
            self.cursor_override_active = False
        self.setToolTip("")
        if self.current_hover_line != -1:
            self.remove_highlighting()
            self.current_hover_line = -1
        super().leaveEvent(event)
    
    def highlight_line(self, line_number):
        """Highlight a specific line"""
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, line_number)
        cursor.select(cursor.SelectionType.LineUnderCursor)
        
        # Create selection format with background color
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor(173, 216, 230))  # Light blue background
        selection.format.setProperty(selection.format.Property.FullWidthSelection, True)
        selection.cursor = cursor
        
        self.setExtraSelections([selection])
    
    def remove_highlighting(self):
        """Remove all highlighting"""
        self.setExtraSelections([])
        
    def show_context_menu(self, position):
        """Show context menu with option to open folder"""
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        selected_line = cursor.selectedText().strip()
        
        # Find the matching folder path
        matching_path = None
        if selected_line:
            # Check exact match first
            if selected_line in self.missing_folders:
                matching_path = selected_line
            else:
                # Check if any stored folder path matches this line
                for folder_path in self.missing_folders:
                    if folder_path.strip() == selected_line or selected_line in folder_path:
                        matching_path = folder_path
                        break
        
        if matching_path:
            menu = QMenu(self)
            
            # Style the context menu
            menu.setStyleSheet("""
                QMenu {
                    background-color: #ffffff;
                    border: 2px solid #e1dfdd;
                    border-radius: 8px;
                    padding: 8px;
                    font-family: 'Segoe UI';
                    font-size: 11px;
                }
                QMenu::item {
                    background-color: transparent;
                    padding: 8px 16px;
                    border-radius: 4px;
                    margin: 2px;
                    color: #323130;
                }
                QMenu::item:selected {
                    background-color: #f3f2f1;
                    border: 1px solid #d2d0ce;
                }
                QMenu::item:hover {
                    background-color: #e1dfdd;
                    color: #0078d4;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #e1dfdd;
                    margin: 4px 8px;
                }
            """)
            
            open_action = QAction("📂 Open Folder in Explorer", self)
            open_action.triggered.connect(lambda: self.open_folder(matching_path))
            menu.addAction(open_action)
            
            menu.addSeparator()
            
            copy_action = QAction("📋 Copy Path", self)
            copy_action.triggered.connect(lambda: self.copy_path(matching_path))
            menu.addAction(copy_action)
            
            menu.exec(self.mapToGlobal(position))
    
    def open_folder(self, folder_path):
        """Open folder in Windows Explorer"""
        try:
            # Normalize path separators for Windows
            normalized_path = os.path.normpath(folder_path)
            
            if os.path.exists(normalized_path):
                # Use Windows Explorer to open the folder - more robust method
                if os.name == 'nt':  # Windows
                    os.startfile(normalized_path)
                else:
                    # Fallback for other systems
                    subprocess.run(['explorer', normalized_path], check=True)
            else:
                QMessageBox.warning(self, "Error", f"Folder no longer exists:\n{normalized_path}")
        except Exception as e:
            # Only show error if it's a real problem, not just subprocess warnings
            if "startfile" not in str(e).lower():
                QMessageBox.critical(self, "Error", f"Failed to open folder:\n{str(e)}")
    
    def copy_path(self, folder_path):
        """Copy folder path to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(folder_path)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to open folder"""
        cursor = self.textCursor()
        cursor.select(cursor.SelectionType.LineUnderCursor)
        selected_line = cursor.selectedText().strip()
        
        # Find the matching folder path
        matching_path = None
        if selected_line:
            # Check exact match first
            if selected_line in self.missing_folders:
                matching_path = selected_line
            else:
                # Check if any stored folder path matches this line
                for folder_path in self.missing_folders:
                    if folder_path.strip() == selected_line or selected_line in folder_path:
                        matching_path = folder_path
                        break
        
        if matching_path:
            self.open_folder(matching_path)
        else:
            super().mouseDoubleClickEvent(event)


class MissingFileScanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scanner_thread = None
        self.init_ui()
        self.apply_modern_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Missing File Scanner")
        self.setGeometry(100, 100, 1000, 1200)
        self.setMinimumSize(850, 1100)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section (fixed size)
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(3)
        
        # Title
        title_label = QLabel("Missing File Scanner")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #323130;")
        header_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Scan folders and subfolders to find where a specific file is missing")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: #605e5c;")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(header_widget)
        
        # Input section (fixed size)
        input_frame = QFrame()
        input_frame.setFixedHeight(380)
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 0px;
            }

        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setSpacing(8)
        input_layout.setContentsMargins(20, 1, 20, 20)
        
        # Input section title
        input_title = QLabel("📁 Scan Configuration")
        input_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        input_title.setStyleSheet("""
            color: #2d3748;
            margin: 0px;
            padding: 0px;
            border: none;
        """)
        input_layout.addWidget(input_title)
        
        # Folder selection card
        folder_card = QFrame()
        folder_card.setMinimumHeight(110)
        folder_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px;
            }

        """)
        
        folder_card_layout = QVBoxLayout(folder_card)
        folder_card_layout.setSpacing(8)
        folder_card_layout.setContentsMargins(6, 6, 6, 6)
        
        folder_label = QLabel("🗂️ Target Folder")
        folder_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        folder_label.setStyleSheet("""
            color: #374151;
            margin: 0px;
            padding: 0px 0px 10px 0px;
            border: none;
        """)
        folder_card_layout.addWidget(folder_label)
        
        folder_input_layout = QHBoxLayout()
        folder_input_layout.setSpacing(8)
        
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Click here or Browse button to select a folder to scan...")
        self.folder_input.setReadOnly(True)
        self.folder_input.setFixedHeight(50)
        self.folder_input.setFont(QFont("Segoe UI", 10))
        self.folder_input.mousePressEvent = lambda event: self.browse_folder()
        self.folder_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px 16px;
                background-color: #f9fafb;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #d1d5db;
                background-color: #ffffff;
            }
        """)
        
        self.browse_button = QPushButton("📂 Browse")
        self.browse_button.clicked.connect(self.browse_folder)
        self.browse_button.setFixedSize(140, 50)
        self.browse_button.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
        """)
        
        folder_input_layout.addWidget(self.folder_input)
        folder_input_layout.addWidget(self.browse_button)
        folder_card_layout.addLayout(folder_input_layout)
        
        input_layout.addWidget(folder_card)
        
        # Filename input card
        filename_card = QFrame()
        filename_card.setMinimumHeight(120)
        filename_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 5px;
            }

        """)
        
        filename_card_layout = QVBoxLayout(filename_card)
        filename_card_layout.setSpacing(8)
        filename_card_layout.setContentsMargins(6, 6, 6, 6)
        
        # Create horizontal layout for side-by-side inputs
        inputs_row_layout = QHBoxLayout()
        inputs_row_layout.setSpacing(12)
        
        # Left column - Filename input
        filename_column = QWidget()
        filename_column_layout = QVBoxLayout(filename_column)
        filename_column_layout.setSpacing(6)
        filename_column_layout.setContentsMargins(0, 0, 0, 0)
        
        filename_label = QLabel("📄 File Name to Search")
        filename_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        filename_label.setStyleSheet("""
            color: #374151;
            margin: 0px;
            padding: 0px 0px 6px 0px;
            border: none;
        """)
        filename_column_layout.addWidget(filename_label)
        
        filename_help = QLabel("Supports full or partial matching with/without extension")
        filename_help.setFont(QFont("Segoe UI", 9))
        filename_help.setStyleSheet("""
            color: #6b7280;
            margin: 0px;
            padding: 0px 0px 10px 0px;
            border: none;
        """)
        filename_column_layout.addWidget(filename_help)
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter filename to search for...")
        self.filename_input.setFixedHeight(50)
        self.filename_input.setFont(QFont("Segoe UI", 10))
        self.filename_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px 16px;
                background-color: #ffffff;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #10b981;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #d1d5db;
            }
        """)
        filename_column_layout.addWidget(self.filename_input)
        
        # Right column - Exclusion input
        exclusion_column = QWidget()
        exclusion_column_layout = QVBoxLayout(exclusion_column)
        exclusion_column_layout.setSpacing(6)
        exclusion_column_layout.setContentsMargins(0, 0, 0, 0)
        
        exclusion_label = QLabel("🚫 Exclude Folders Containing")
        exclusion_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        exclusion_label.setStyleSheet("""
            color: #374151;
            margin: 0px;
            padding: 0px 0px 6px 0px;
            border: none;
        """)
        exclusion_column_layout.addWidget(exclusion_label)
        
        exclusion_help = QLabel("Comma-separated list (e.g., temp, cache, .git)")
        exclusion_help.setFont(QFont("Segoe UI", 9))
        exclusion_help.setStyleSheet("""
            color: #6b7280;
            margin: 0px;
            padding: 0px 0px 10px 0px;
            border: none;
        """)
        exclusion_column_layout.addWidget(exclusion_help)
        
        self.exclusion_input = QLineEdit()
        self.exclusion_input.setPlaceholderText("Optional: folders to skip...")
        self.exclusion_input.setFixedHeight(50)
        self.exclusion_input.setFont(QFont("Segoe UI", 10))
        self.exclusion_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px 16px;
                background-color: #ffffff;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #ef4444;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #d1d5db;
            }
        """)
        exclusion_column_layout.addWidget(self.exclusion_input)
        
        # Add columns to horizontal layout
        inputs_row_layout.addWidget(filename_column)
        inputs_row_layout.addWidget(exclusion_column)
        
        filename_card_layout.addLayout(inputs_row_layout)
        
        input_layout.addWidget(filename_card)
        
        main_layout.addWidget(input_frame)
        
        # Button section (fixed size)
        button_widget = QWidget()
        button_widget.setFixedHeight(60)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 10)
        button_layout.addStretch()
        
        self.scan_button = QPushButton("🔍 Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setFixedSize(180, 50)
        self.scan_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.scan_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px 15px;
                font-weight: 700;

            }
            QPushButton:hover {
                background-color: #10b981;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #d1d5db;
                color: #9ca3af;
            }
        """)
        
        button_layout.addWidget(self.scan_button)
        button_layout.addStretch()
        
        main_layout.addWidget(button_widget)
        
        # Progress bar (fixed size)
        progress_widget = QWidget()
        progress_widget.setFixedHeight(35)
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e1dfdd;
                border-radius: 10px;
                background-color: #f3f2f1;
                text-align: center;
                font-weight: bold;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 8px;
                margin: 0px;
                border: none;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(progress_widget)
        
        # Results section (expandable)
        results_label = QLabel("Folders Missing the File (Double-click or right-click to open):")
        results_label.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
        results_label.setStyleSheet("color: #323130;")
        main_layout.addWidget(results_label)
        
        # Results text area (takes remaining space)
        self.results_text = ClickableTextEdit()
        self.results_text.setFont(QFont("Consolas", 10))
        self.results_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e1dfdd;
                border-radius: 8px;
                background-color: white;
                color: #323130;
                padding: 15px;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        self.results_text.setPlaceholderText("Scan results will appear here...\nDouble-click any path to open in Explorer, or right-click for more options.")
        main_layout.addWidget(self.results_text, 2)  # This takes remaining space with higher priority
        
        # Status section (fixed size)
        status_widget = QWidget()
        status_widget.setFixedHeight(25)
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(0, 5, 0, 0)
        
        self.status_label = QLabel("Ready to scan")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #605e5c;")
        status_layout.addWidget(self.status_label)
        
        main_layout.addWidget(status_widget)
        
    def apply_modern_theme(self):
        """Apply modern Windows 11-like theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QWidget {
                background-color: #ffffff;
                color: #323130;
            }
        """)
        
    def browse_folder(self):
        """Open folder browser dialog"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Folder to Scan",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        if folder:
            self.folder_input.setText(folder)
            
    def start_scan(self):
        """Start the file scanning process"""
        folder_path = self.folder_input.text().strip()
        filename = self.filename_input.text().strip()
        exclusion_text = self.exclusion_input.text().strip()
        
        if not folder_path:
            QMessageBox.warning(self, "Warning", "Please select a folder to scan.")
            return
            
        if not filename:
            QMessageBox.warning(self, "Warning", "Please enter a filename to search for.")
            return
            
        if not os.path.exists(folder_path):
            QMessageBox.critical(self, "Error", "Selected folder does not exist.")
            return
        
        # Parse exclusion list
        exclusion_list = []
        if exclusion_text:
            exclusion_list = [term.strip() for term in exclusion_text.split(',') if term.strip()]
        
        # Clear previous results
        self.results_text.clear_results()
        
        # Setup UI for scanning - reset progress bar for new scan
        self.scan_button.setEnabled(False)
        self.scan_button.setText("Scanning...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)  # Reset to 0 for new scan
        self.status_label.setText("Initializing scan...")
        
        # Start scanner thread
        self.scanner_thread = FileScannerThread(folder_path, filename, exclusion_list)
        self.scanner_thread.progress_updated.connect(self.update_progress)
        self.scanner_thread.folder_found.connect(self.add_missing_folder)
        self.scanner_thread.scan_completed.connect(self.scan_finished)
        self.scanner_thread.start()
        
    def update_progress(self, current, total):
        """Update progress bar and status"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Scanning... {current}/{total} folders checked")
        
    def add_missing_folder(self, folder_path):
        """Add a folder to the results where the file is missing"""
        self.results_text.add_folder_path(folder_path)
        
    def scan_finished(self, missing_count):
        """Handle scan completion"""
        self.scan_button.setEnabled(True)
        self.scan_button.setText("🔍 Start Scan")
        # Keep progress bar visible at 100% - don't hide it
        
        exclusion_text = self.exclusion_input.text().strip()
        exclusion_info = ""
        if exclusion_text:
            exclusion_list = [term.strip() for term in exclusion_text.split(',') if term.strip()]
            exclusion_info = f"\nExcluded folders containing: {', '.join(exclusion_list)}"
        
        if missing_count == 0:
            self.status_label.setText("✅ File found in all folders!")
            self.results_text.setText("Great! The file was found in all scanned folders.")
        else:
            self.status_label.setText(f"❌ File missing in {missing_count} folder(s)")
            
        # Show completion message
        QMessageBox.information(
            self, 
            "Scan Complete", 
            f"Scan completed!\n\nFile missing in {missing_count} folder(s).{exclusion_info}"
        )


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Missing File Scanner")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("File Scanner Tools")
    
    # Apply Windows 11 style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = MissingFileScanner()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 