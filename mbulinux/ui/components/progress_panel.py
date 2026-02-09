"""
Widget for displaying write progress.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QTextEdit, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QTextCursor, QIcon

from ...ui.resources import get_icon

class ProgressPanel(QWidget):
    """Widget for displaying write progress."""
    
    def __init__(self):
        super().__init__()
        
        self.setup_ui()
        self.reset()
    
    def setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("Creating Bootable USB")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        # Cancel button
        self.cancel_button = QPushButton()
        self.cancel_button.setIcon(get_icon("process-stop"))
        self.cancel_button.setToolTip("Cancel operation")
        self.cancel_button.hide()  # Not implemented yet
        header_layout.addWidget(self.cancel_button)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Details button
        self.details_button = QPushButton("Show Details")
        self.details_button.setIcon(get_icon("arrow-down"))
        self.details_button.clicked.connect(self.toggle_details)
        layout.addWidget(self.details_button)
        
        # Log text edit (hidden by default)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.hide()
        layout.addWidget(self.log_text)
    
    def reset(self):
        """Reset progress display."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.log_text.clear()
        self.show_details(False)
    
    @Slot(int, str)
    def update_progress(self, percent: int, message: str):
        """Update progress display."""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
        
        # Add to log
        self.add_log(message)
        
        # Update title based on progress
        if percent == 0:
            self.title_label.setText("Preparing...")
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #0078d7;")
        elif percent < 100:
            self.title_label.setText("Writing...")
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff9900;")
        else:
            self.title_label.setText("Completed!")
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00aa00;")
    
    def add_log(self, message: str):
        """Add message to log."""
        self.log_text.append(f"{message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def toggle_details(self):
        """Toggle details visibility."""
        current = self.log_text.isVisible()
        self.show_details(not current)
    
    def show_details(self, show: bool):
        """Show or hide details."""
        if show:
            self.log_text.show()
            self.details_button.setText("Hide Details")
            self.details_button.setIcon(get_icon("arrow-up"))
        else:
            self.log_text.hide()
            self.details_button.setText("Show Details")
            self.details_button.setIcon(get_icon("arrow-down"))
    
    def set_cancelable(self, cancelable: bool):
        """Set whether operation can be cancelled."""
        self.cancel_button.setVisible(cancelable)