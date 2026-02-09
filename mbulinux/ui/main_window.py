"""
Main application window.
"""

import sys
import json
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QIcon

from ..constants import APP_NAME, CONFIG_DIR
from ..core.disk_manager import DiskManager
from ..core.image_analyzer import ImageAnalyzer
from ..core.permissions import PermissionManager

from .components.disk_list_widget import DiskListWidget
from .components.iso_selector import IsoSelector
from .components.settings_panel import SettingsPanel
from .components.progress_panel import ProgressPanel
from .resources import load_style, get_icon

class MainWindow(QMainWindow):
    """Main application window."""
    
    # Signals
    write_started = Signal()
    write_finished = Signal(bool, str)
    progress_updated = Signal(int, str)
    
    def __init__(self, settings: dict):
        super().__init__()
        
        self.settings = settings
        self.iso_path: Optional[str] = None
        self.selected_device: Optional[str] = None
        self.current_strategy = None
        
        # Initialize managers
        self.disk_manager = DiskManager()
        self.image_analyzer = ImageAnalyzer()
        self.permission_manager = PermissionManager()
        
        # Setup UI
        self.setup_ui()
        
        # Connect signals
        self.connect_signals()
        
        # Setup auto-refresh
        self.setup_refresh_timer()
        
        # Apply settings
        self.apply_settings()
    
    def setup_ui(self):
        """Setup the main window UI."""
        # Window properties
        self.setWindowTitle(f"{APP_NAME} - Make Bootable USB on Linux")
        self.setWindowIcon(get_icon("usb"))
        
        # Set window size from settings or default
        width = self.settings.get('window_width', 900)
        height = self.settings.get('window_height', 700)
        self.resize(width, height)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (ISO selection and settings)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # ISO selector
        self.iso_selector = IsoSelector()
        left_layout.addWidget(self.iso_selector)
        
        # Settings panel
        self.settings_panel = SettingsPanel()
        left_layout.addWidget(self.settings_panel)
        
        # Add stretch
        left_layout.addStretch()
        
        # Right panel (Disk selection)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Disk list
        self.disk_list = DiskListWidget()
        right_layout.addWidget(self.disk_list)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (60% left, 40% right)
        splitter.setSizes([int(width * 0.6), int(width * 0.4)])
        
        main_layout.addWidget(splitter)
        
        # Progress panel (hidden by default)
        self.progress_panel = ProgressPanel()
        self.progress_panel.hide()
        main_layout.addWidget(self.progress_panel)
        
        # Start button
        from PySide6.QtWidgets import QPushButton
        self.start_button = QPushButton("Start Creating Bootable USB")
        self.start_button.setIcon(get_icon("media-flash"))
        self.start_button.setEnabled(False)
        main_layout.addWidget(self.start_button)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def connect_signals(self):
        """Connect UI signals to slots."""
        # ISO selection
        self.iso_selector.iso_selected.connect(self.on_iso_selected)
        
        # Disk selection
        self.disk_list.disk_selected.connect(self.on_disk_selected)
        self.disk_list.refresh_requested.connect(self.refresh_disks)
        
        # Start button
        self.start_button.clicked.connect(self.start_write_process)
        
        # Progress signals
        self.progress_updated.connect(self.progress_panel.update_progress)
        self.write_started.connect(self.on_write_started)
        self.write_finished.connect(self.on_write_finished)
    
    def setup_refresh_timer(self):
        """Setup timer for automatic disk refresh."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_disks)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def apply_settings(self):
        """Apply application settings."""
        # Apply theme
        theme = self.settings.get('theme', 'light')
        style = load_style(theme)
        self.setStyleSheet(style)
        
        # Apply language
        # TODO: Implement language switching
    
    def refresh_disks(self):
        """Refresh the list of available disks."""
        try:
            disks = self.disk_manager.get_removable_disks()
            self.disk_list.update_disks(disks)
            
            # Update status
            count = len(disks)
            self.status_bar.showMessage(f"Found {count} removable disk(s)")
        except Exception as e:
            self.status_bar.showMessage(f"Error refreshing disks: {str(e)}")
    
    @Slot(str)
    def on_iso_selected(self, iso_path: str):
        """Handle ISO file selection."""
        self.iso_path = iso_path
        
        # Analyze ISO
        try:
            iso_info = self.image_analyzer.analyze(iso_path)
            self.settings_panel.set_iso_info(iso_info)
            
            # Update status
            size_gb = iso_info['size'] / (1024**3)
            self.status_bar.showMessage(
                f"Selected: {iso_info['os_name']} ISO ({size_gb:.1f} GB)"
            )
            
            # Auto-select appropriate settings
            self.auto_select_settings(iso_info)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to analyze ISO: {str(e)}")
            self.iso_path = None
        
        self.update_start_button()
    
    @Slot(dict)
    def on_disk_selected(self, disk_info: dict):
        """Handle disk selection."""
        self.selected_device = disk_info.get('device')
        
        # Update status
        if self.selected_device:
            size_gb = disk_info.get('size_gb', 0)
            model = disk_info.get('model', 'Unknown')
            self.status_bar.showMessage(
                f"Selected: {model} ({size_gb:.1f} GB) at {self.selected_device}"
            )
        
        self.update_start_button()
    
    def auto_select_settings(self, iso_info: dict):
        """Auto-select settings based on ISO type."""
        iso_type = iso_info.get('type')
        
        if iso_type == 2:  # Windows
            # Windows needs GPT for UEFI
            self.settings_panel.set_partition_scheme('gpt')
            
            # Check WIM size
            wim_size = iso_info.get('wim_size', 0)
            if wim_size > 4 * 1024**3:  # > 4GB
                # Need NTFS for large WIM
                self.settings_panel.set_filesystem('ntfs')
            else:
                # FAT32 works for small WIM
                self.settings_panel.set_filesystem('fat32')
        
        elif iso_type == 1:  # Linux
            # Most Linux ISOs work with both MBR and GPT
            self.settings_panel.set_partition_scheme('gpt')
            self.settings_panel.set_filesystem('fat32')
    
    def update_start_button(self):
        """Update start button state based on selections."""
        enabled = bool(self.iso_path and self.selected_device)
        self.start_button.setEnabled(enabled)
        
        if enabled:
            self.start_button.setText("Start Creating Bootable USB")
        else:
            if not self.iso_path and not self.selected_device:
                self.start_button.setText("Select ISO file and USB drive")
            elif not self.iso_path:
                self.start_button.setText("Select ISO file")
            else:
                self.start_button.setText("Select USB drive")
    
    def start_write_process(self):
        """Start the USB creation process."""
        if not self.iso_path or not self.selected_device:
            return
        
        # Get settings
        settings = self.settings_panel.get_settings()
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm USB Creation",
            f"This will erase ALL data on {self.selected_device}\n"
            f"ISO: {Path(self.iso_path).name}\n"
            f"Device: {self.selected_device}\n\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Check permissions
        if not self.permission_manager.request_permissions():
            QMessageBox.critical(
                self,
                "Permission Error",
                "Insufficient permissions to write to USB device.\n"
                "Please run with administrator privileges."
            )
            return
        
        # Start write process
        self.write_started.emit()
    
    @Slot()
    def on_write_started(self):
        """Handle write process start."""
        # Disable UI
        self.iso_selector.setEnabled(False)
        self.disk_list.setEnabled(False)
        self.settings_panel.setEnabled(False)
        self.start_button.setEnabled(False)
        
        # Show progress panel
        self.progress_panel.show()
        self.progress_panel.reset()
        
        # Start actual write in background
        QTimer.singleShot(100, self.perform_write)
    
    def perform_write(self):
        """Perform the actual write operation."""
        try:
            # Get strategy based on ISO type
            iso_info = self.image_analyzer.analyze(self.iso_path)
            iso_type = iso_info.get('type')
            
            if iso_type == 2:  # Windows
                from ..core.writer_strategies.windows_strategy import WindowsWriteStrategy
                strategy = WindowsWriteStrategy()
            else:  # Linux and others
                from ..core.writer_strategies.linux_strategy import LinuxWriteStrategy
                strategy = LinuxWriteStrategy()
            
            # Set progress callback
            strategy.set_progress_callback(
                lambda p, m: self.progress_updated.emit(p, m)
            )
            
            # Get settings
            settings = self.settings_panel.get_settings()
            
            # Perform write
            success = strategy.write(
                self.iso_path,
                self.selected_device,
                settings
            )
            
            # Emit result
            message = "Write completed successfully" if success else "Write failed"
            self.write_finished.emit(success, message)
            
        except Exception as e:
            self.write_finished.emit(False, f"Error: {str(e)}")
    
    @Slot(bool, str)
    def on_write_finished(self, success: bool, message: str):
        """Handle write process completion."""
        # Re-enable UI
        self.iso_selector.setEnabled(True)
        self.disk_list.setEnabled(True)
        self.settings_panel.setEnabled(True)
        self.update_start_button()
        
        # Hide progress panel after delay
        QTimer.singleShot(3000, self.progress_panel.hide)
        
        # Show result message
        if success:
            QMessageBox.information(self, "Success", message)
            self.status_bar.showMessage("USB created successfully")
        else:
            QMessageBox.critical(self, "Error", message)
            self.status_bar.showMessage("USB creation failed")
        
        # Refresh disk list
        self.refresh_disks()
    
    def get_current_settings(self) -> dict:
        """Get current window settings."""
        return {
            'window_width': self.width(),
            'window_height': self.height(),
            'theme': self.settings.get('theme', 'light'),
        }
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        # Save window size
        self.settings['window_width'] = self.width()
        self.settings['window_height'] = self.height()
        
        # Stop refresh timer
        self.refresh_timer.stop()
        
        # Accept close event
        event.accept()