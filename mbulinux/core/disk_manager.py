"""
Disk management using UDisks2.
"""

import subprocess
import json
import re
from typing import List, Dict, Optional
from pathlib import Path

import pydbus
from gi.repository import GLib

class DiskManager:
    """Manage disks using UDisks2."""
    
    def __init__(self):
        self.bus = pydbus.SystemBus()
        try:
            self.udisks = self.bus.get('org.freedesktop.UDisks2', '/org/freedesktop/UDisks2')
        except KeyError:
            raise RuntimeError("UDisks2 service not available. Please install udisks2.")

    def _decode_udisks_value(self, value):
        """Decode UDisks byte arrays (often lists of ints) into strings."""
        if isinstance(value, (bytes, bytearray)):
            return value.decode('utf-8', errors='ignore').strip('\x00')
        if isinstance(value, list):
            try:
                return bytes(value).decode('utf-8', errors='ignore').strip('\x00')
            except Exception:
                return value
        return value

    def _decode_mount_points(self, mount_points):
        """Decode list of mount points from UDisks."""
        decoded = []
        for mp in mount_points or []:
            decoded_mp = self._decode_udisks_value(mp)
            if isinstance(decoded_mp, str) and decoded_mp:
                decoded.append(decoded_mp)
        return decoded
    
    def get_removable_disks(self) -> List[Dict]:
        """
        Get list of removable disks (USB drives).
        
        Returns:
            List of dictionaries with disk information
        """
        disks = []
        
        try:
            # Get all block devices
            objects = self.udisks.GetManagedObjects()
            
            for obj_path, interfaces in objects.items():
                if 'org.freedesktop.UDisks2.Block' in interfaces:
                    block = interfaces['org.freedesktop.UDisks2.Block']
                    drive_path = block.get('Drive', '/')
                    
                    # Get drive info
                    drive_interfaces = objects.get(drive_path, {})
                    if 'org.freedesktop.UDisks2.Drive' in drive_interfaces:
                        drive = drive_interfaces['org.freedesktop.UDisks2.Drive']
                        
                        # Only removable drives
                        if drive.get('Removable', False):
                            raw_device = block.get('Device', '/dev/unknown')
                            device = self._decode_udisks_value(raw_device)
                            if not isinstance(device, str):
                                device = '/dev/unknown'

                            disk_info = {
                                'device': device,
                                'path': obj_path,
                                'size': block.get('Size', 0),
                                'model': drive.get('Model', 'Unknown'),
                                'vendor': drive.get('Vendor', 'Unknown'),
                                'serial': drive.get('Serial', ''),
                                'read_only': block.get('ReadOnly', False),
                                'mount_points': self._decode_mount_points(block.get('MountPoints', [])),
                                'partition_table': block.get('PartitionTable', {}),
                                'is_partition': 'org.freedesktop.UDisks2.Partition' in interfaces,
                            }
                            
                            # Convert size to GB
                            disk_info['size_gb'] = disk_info['size'] / (1024**3)
                            
                            # Only add if it's a whole disk (not partition)
                            if not disk_info['is_partition']:
                                disks.append(disk_info)
        except Exception as e:
            print(f"Error getting disks: {e}")
            # Fallback to lsblk
            disks = self._get_disks_fallback()
        
        return disks
    
    def _get_disks_fallback(self) -> List[Dict]:
        """Fallback method using lsblk if UDisks2 fails."""
        try:
            result = subprocess.run(
                ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MODEL,VENDOR,RO,MOUNTPOINT,PKNAME'],
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            disks = []
            
            for device in data.get('blockdevices', []):
                if device.get('type') == 'disk' and device.get('pkname') is None:
                    # Check if removable (simple heuristic)
                    model = device.get('model', '')
                    if any(keyword in model.lower() for keyword in ['usb', 'flash', 'cruzer']):
                        disks.append({
                            'device': f"/dev/{device['name']}",
                            'model': model,
                            'vendor': device.get('vendor', ''),
                            'size': 0,  # Would need parsing
                            'size_gb': self._parse_size(device.get('size', '0')),
                            'read_only': device.get('ro', '0') == '1',
                            'mount_points': [device.get('mountpoint')] if device.get('mountpoint') else [],
                        })
            
            return disks
        except Exception as e:
            print(f"Fallback also failed: {e}")
            return []
    
    def _parse_size(self, size_str: str) -> float:
        """Parse size string like '14.9G' to GB."""
        match = re.match(r'([\d.]+)([KMGTP])', size_str.upper())
        if not match:
            return 0.0
        
        value, unit = match.groups()
        value = float(value)
        
        units = {'K': 1/1024/1024, 'M': 1/1024, 'G': 1, 'T': 1024, 'P': 1024*1024}
        return value * units.get(unit, 1)
    
    def get_disk_usage(self, device: str) -> Dict:
        """Get disk usage information."""
        try:
            result = subprocess.run(
                ['df', '-h', device],
                capture_output=True,
                text=True,
                check=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    return {
                        'size': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'use_percent': parts[4],
                        'mounted_on': parts[5] if len(parts) > 5 else ''
                    }
        except subprocess.CalledProcessError:
            pass
        
        return {}
    
    def unmount_disk(self, device: str) -> bool:
        """Unmount a disk."""
        try:
            # Try through UDisks2 first
            obj = self.bus.get('org.freedesktop.UDisks2', device.replace('/dev/', '/org/freedesktop/UDisks2/block_devices/'))
            obj.Filesystem.Unmount({})
            return True
        except Exception:
            # Fallback to umount
            try:
                subprocess.run(['umount', device], check=True)
                return True
            except subprocess.CalledProcessError:
                return False
    
    def eject_disk(self, device: str) -> bool:
        """Eject a disk."""
        try:
            obj = self.bus.get('org.freedesktop.UDisks2', device.replace('/dev/', '/org/freedesktop/UDisks2/block_devices/'))
            obj.Drive.Eject({})
            return True
        except Exception as e:
            print(f"Failed to eject {device}: {e}")
            return False
