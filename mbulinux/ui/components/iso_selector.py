"""
Widget for selecting ISO files.
"""

import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon

from ...ui.resources import get_icon

class IsoSelector(QWidget):
    """Widget for selecting ISO image files."""
    
    # Signals
    iso_selected = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        self.iso_path = None
        
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("ISO Image File")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # ISO info
        self.info_label = QLabel("No ISO file selected")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.info_label)
        
        # Path display
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("No file selected")
        layout.addWidget(self.path_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setIcon(get_icon("folder-open"))
        self.browse_button.clicked.connect(self.browse_iso)
        button_layout.addWidget(self.browse_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setIcon(get_icon("edit-clear"))
        self.clear_button.clicked.connect(self.clear_selection)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # Drop hint
        self.drop_hint = QLabel("← Drag and drop ISO file here")
        self.drop_hint.setAlignment(Qt.AlignCenter)
        self.drop_hint.setStyleSheet("""
            QLabel {
                color: #888888;
                font-style: italic;
                border: 2px dashed #cccccc;
                border-radius: 5px;
                padding: 20px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.drop_hint)
    
    def browse_iso(self):
        """Open file dialog to select ISO."""
        file_filter = "ISO Images (*.iso *.img);;All Files (*.*)"
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select ISO Image",
            str(Path.home()),
            file_filter
        )
        
        if file_path:
            self.set_iso_path(file_path)
    
    def set_iso_path(self, file_path: str):
        """Set ISO file path."""
        if not os.path.exists(file_path):
            self.show_error(f"File not found: {file_path}")
            return
        
        if not file_path.lower().endswith(('.iso', '.img')):
            self.show_warning("Selected file doesn't appear to be an ISO image")
        
        self.iso_path = file_path
        self.path_edit.setText(file_path)
        
        # Update info
        file_name = Path(file_path).name
        file_size = os.path.getsize(file_path) / (1024**3)  # GB
        
        self.info_label.setText(
            f"Selected: {file_name}\n"
            f"Size: {file_size:.2f} GB"
        )
        self.info_label.setStyleSheet("color: #333333; font-style: normal;")
        
        # Emit signal
        self.iso_selected.emit(file_path)
    
    def clear_selection(self):
        """Clear ISO selection."""
        self.iso_path = None
        self.path_edit.clear()
        self.info_label.setText("No ISO file selected")
        self.info_label.setStyleSheet("color: #666666; font-style: italic;")
        
        # Emit empty signal
        self.iso_selected.emit("")
    
    def get_iso_path(self) -> str:
        """Get selected ISO path."""
        return self.iso_path
    
    def show_error(self, message: str):
        """Show error message."""
        self.info_label.setText(f"Error: {message}")
        self.info_label.setStyleSheet("color: #cc0000; font-style: italic;")
    
    def show_warning(self, message: str):
        """Show warning message."""
        self.info_label.setText(f"Warning: {message}")
        self.info_label.setStyleSheet("color: #ff9900; font-style: italic;")
    
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(('.iso', '.img')):
                event.acceptProposedAction()
                self.drop_hint.setStyleSheet("""
                    QLabel {
                        color: #0078d7;
                        font-style: italic;
                        border: 2px dashed #0078d7;
                        border-radius: 5px;
                        padding: 20px;
                        margin-top: 10px;
                        background-color: #f0f7ff;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.drop_hint.setStyleSheet("""
            QLabel {
                color: #888888;
                font-style: italic;
                border: 2px dashed #cccccc;
                border-radius: 5px;
                padding: 20px;
                margin-top: 10px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.iso', '.img')):
                self.set_iso_path(file_path)
        
        # Reset drop hint
        self.drop_hint.setStyleSheet("""
            QLabel {
                color: #888888;
                font-style: italic;
                border: 2px dashed #cccccc;
                border-radius: 5px;
                padding: 20px;
                margin-top: 10px;
            }
        """)