"""
Widget for configuration settings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout,
    QComboBox, QCheckBox, QLabel, QFrame
)
from PySide6.QtCore import Signal

from ...constants import SCHEME_MBR, SCHEME_GPT, FS_FAT32, FS_NTFS, FS_EXFAT

class SettingsPanel(QWidget):
    """Widget for configuration settings."""
    
    def __init__(self):
        super().__init__()
        
        self.iso_info = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("Settings")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # ISO Info group
        self.info_group = QGroupBox("ISO Information")
        info_layout = QFormLayout(self.info_group)
        
        self.os_label = QLabel("Unknown")
        info_layout.addRow("Operating System:", self.os_label)
        
        self.arch_label = QLabel("Unknown")
        info_layout.addRow("Architecture:", self.arch_label)
        
        self.type_label = QLabel("Unknown")
        info_layout.addRow("Type:", self.type_label)
        
        layout.addWidget(self.info_group)
        
        # Formatting group
        self.format_group = QGroupBox("Formatting Options")
        format_layout = QFormLayout(self.format_group)
        
        # Partition scheme
        self.scheme_combo = QComboBox()
        self.scheme_combo.addItem("MBR (Legacy BIOS)", SCHEME_MBR)
        self.scheme_combo.addItem("GPT (UEFI)", SCHEME_GPT)
        format_layout.addRow("Partition Scheme:", self.scheme_combo)
        
        # Filesystem
        self.fs_combo = QComboBox()
        self.fs_combo.addItem("FAT32", FS_FAT32)
        self.fs_combo.addItem("NTFS", FS_NTFS)
        self.fs_combo.addItem("exFAT", FS_EXFAT)
        format_layout.addRow("Filesystem:", self.fs_combo)
        
        layout.addWidget(self.format_group)
        
        # Options group
        self.options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(self.options_group)
        
        self.quick_format_check = QCheckBox("Quick format")
        self.quick_format_check.setChecked(True)
        options_layout.addWidget(self.quick_format_check)
        
        self.validate_check = QCheckBox("Validate after write")
        self.validate_check.setChecked(True)
        options_layout.addWidget(self.validate_check)
        
        self.eject_check = QCheckBox("Eject USB when done")
        self.eject_check.setChecked(False)
        options_layout.addWidget(self.eject_check)
        
        layout.addWidget(self.options_group)
        
        # Add stretch
        layout.addStretch()
    
    def set_iso_info(self, iso_info: dict):
        """Set ISO information."""
        self.iso_info = iso_info
        
        # Update labels
        self.os_label.setText(iso_info.get('os_name', 'Unknown'))
        self.arch_label.setText(iso_info.get('architecture', 'Unknown'))
        
        # Set type
        iso_type = iso_info.get('type', 0)
        type_names = {
            0: "Unknown",
            1: "Linux",
            2: "Windows",
            3: "macOS",
            4: "Hybrid"
        }
        self.type_label.setText(type_names.get(iso_type, "Unknown"))
        
        # Enable/disable options based on ISO type
        self.update_options_for_iso(iso_info)
    
    def update_options_for_iso(self, iso_info: dict):
        """Update available options based on ISO type."""
        iso_type = iso_info.get('type', 0)
        
        if iso_type == 2:  # Windows
            # Windows requires specific settings
            self.scheme_combo.setCurrentIndex(1)  # GPT for UEFI
            
            # Check WIM size
            wim_size = iso_info.get('wim_size', 0)
            if wim_size > 4 * 1024**3:  # > 4GB
                # Need NTFS for large WIM
                self.fs_combo.setCurrentIndex(1)  # NTFS
                # Disable FAT32
                for i in range(self.fs_combo.count()):
                    if self.fs_combo.itemData(i) == FS_FAT32:
                        self.fs_combo.model().item(i).setEnabled(False)
            else:
                # Enable all filesystems
                for i in range(self.fs_combo.count()):
                    self.fs_combo.model().item(i).setEnabled(True)
        
        elif iso_type == 1:  # Linux
            # Enable all options for Linux
            for i in range(self.fs_combo.count()):
                self.fs_combo.model().item(i).setEnabled(True)
    
    def set_partition_scheme(self, scheme: str):
        """Set partition scheme."""
        index = self.scheme_combo.findData(scheme)
        if index >= 0:
            self.scheme_combo.setCurrentIndex(index)
    
    def set_filesystem(self, filesystem: str):
        """Set filesystem."""
        index = self.fs_combo.findData(filesystem)
        if index >= 0:
            self.fs_combo.setCurrentIndex(index)
    
    def get_settings(self) -> dict:
        """Get current settings."""
        return {
            'scheme': self.scheme_combo.currentData(),
            'filesystem': self.fs_combo.currentData(),
            'quick_format': self.quick_format_check.isChecked(),
            'validate': self.validate_check.isChecked(),
            'eject': self.eject_check.isChecked(),
            'iso_info': self.iso_info
        }