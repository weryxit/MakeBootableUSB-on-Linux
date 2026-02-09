"""
Tests for disk manager.
"""

import pytest
from unittest.mock import Mock, patch
from mbulinux.core.disk_manager import DiskManager

def test_disk_manager_initialization():
    """Test DiskManager initialization."""
    with patch('pydbus.SystemBus') as mock_bus:
        mock_bus.return_value.get.return_value = Mock()
        manager = DiskManager()
        assert manager is not None

def test_get_removable_disks_empty():
    """Test getting removable disks when none are available."""
    with patch('pydbus.SystemBus') as mock_bus:
        mock_udisks = Mock()
        mock_udisks.GetManagedObjects.return_value = {}
        mock_bus.return_value.get.return_value = mock_udisks
        
        manager = DiskManager()
        disks = manager.get_removable_disks()
        
        assert disks == []

def test_disk_unmount_success():
    """Test successful disk unmount."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        
        manager = DiskManager()
        success = manager.unmount_disk("/dev/sdb1")
        
        assert success is True

def test_disk_unmount_failure():
    """Test failed disk unmount."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = Exception("Failed")
        
        manager = DiskManager()
        success = manager.unmount_disk("/dev/sdb1")
        
        assert success is False

def test_parse_size():
    """Test size string parsing."""
    manager = DiskManager()
    
    # Test GB
    assert manager._parse_size("14.9G") == 14.9
    
    # Test MB
    assert manager._parse_size("1024M") == 1.0
    
    # Test invalid
    assert manager._parse_size("invalid") == 0.0