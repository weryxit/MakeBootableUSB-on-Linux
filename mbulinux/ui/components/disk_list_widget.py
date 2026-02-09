"""
Widget for displaying and selecting disks.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
    QListWidgetItem, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QIcon, QFont

from ...ui.resources import get_icon

class DiskListWidget(QWidget):
    """Widget for displaying list of removable disks."""
    
    # Signals
    disk_selected = Signal(dict)
    refresh_requested = Signal()
    
    def __init__(self):
        super().__init__()
        
        self.disks = []
        self.selected_disk = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Available USB Drives")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(get_icon("view-refresh"))
        self.refresh_button.setToolTip("Refresh disk list")
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Disk list
        self.disk_list = QListWidget()
        self.disk_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.disk_list)
        
        # No disks label
        self.no_disks_label = QLabel("No USB drives detected")
        self.no_disks_label.setAlignment(Qt.AlignCenter)
        self.no_disks_label.setStyleSheet("color: #666666; font-style: italic;")
        self.no_disks_label.hide()
        layout.addWidget(self.no_disks_label)
    
    def update_disks(self, disks: list):
        """Update the list of disks."""
        self.disks = disks
        self.disk_list.clear()
        
        if not disks:
            self.no_disks_label.show()
            self.disk_list.hide()
            self.selected_disk = None
            return
        
        self.no_disks_label.hide()
        self.disk_list.show()
        
        for disk in disks:
            item = self.create_disk_item(disk)
            self.disk_list.addItem(item)
    
    def create_disk_item(self, disk: dict) -> QListWidgetItem:
        """Create a list item for a disk."""
        device = disk.get('device', 'Unknown')
        model = disk.get('model', 'Unknown Drive')
        size_gb = disk.get('size_gb', 0)
        vendor = disk.get('vendor', '')
        
        # Create item text
        text = f"{model}\n"
        if vendor and vendor != 'Unknown':
            text += f"{vendor} • "
        text += f"{size_gb:.1f} GB • {device}"
        
        # Create item
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, disk)
        
        # Set icon
        item.setIcon(get_icon("drive-removable-media"))
        
        # Set tooltip
        tooltip = f"Device: {device}\n"
        tooltip += f"Model: {model}\n"
        tooltip += f"Size: {size_gb:.1f} GB\n"
        tooltip += f"Vendor: {vendor}\n"
        
        if disk.get('read_only', False):
            tooltip += "Status: Read-only"
            item.setForeground(Qt.darkGray)
        else:
            tooltip += "Status: Read-write"
        
        item.setToolTip(tooltip)
        
        return item
    
    @Slot()
    def on_selection_changed(self):
        """Handle disk selection change."""
        selected_items = self.disk_list.selectedItems()
        
        if not selected_items:
            self.selected_disk = None
            return
        
        item = selected_items[0]
        disk = item.data(Qt.UserRole)
        self.selected_disk = disk
        
        # Emit signal
        self.disk_selected.emit(disk)
    
    def get_selected_disk(self) -> dict:
        """Get currently selected disk."""
        return self.selected_disk
    
    def clear_selection(self):
        """Clear disk selection."""
        self.disk_list.clearSelection()
        self.selected_disk = None