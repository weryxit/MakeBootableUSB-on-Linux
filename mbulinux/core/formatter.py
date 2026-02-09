"""
Disk formatting functionality.
"""

import subprocess
import time
from typing import Dict, Optional

class DiskFormatter:
    """Handle disk formatting operations."""
    
    def __init__(self):
        pass
    
    def format_disk(self, device: str, options: Dict) -> bool:
        """
        Format a disk with given options.
        
        Args:
            device: Block device path (e.g., /dev/sdb)
            options: {
                'scheme': 'mbr' or 'gpt',
                'filesystem': 'fat32', 'ntfs', 'exfat',
                'label': str (optional),
                'quick': bool (default: False)
            }
            
        Returns:
            True if successful
        """
        try:
            # Unmount device first
            self._unmount_device(device)
            
            # Create partition table
            scheme = options.get('scheme', 'gpt')
            self._create_partition_table(device, scheme)
            
            # Create partition
            fs_type = options.get('filesystem', 'fat32')
            self._create_partition(device, fs_type, scheme)
            
            # Format partition
            label = options.get('label', 'BOOTUSB')
            quick = options.get('quick', False)
            
            partition = f"{device}1"
            time.sleep(1)  # Wait for partition to appear
            
            return self._format_partition(partition, fs_type, label, quick)
            
        except subprocess.CalledProcessError as e:
            print(f"Formatting failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def _unmount_device(self, device: str):
        """Unmount device and all partitions."""
        try:
            # Try udisksctl first
            subprocess.run(['udisksctl', 'unmount', '-b', device],
                          capture_output=True, check=False)
            
            # Also try regular umount
            subprocess.run(['umount', device], capture_output=True, check=False)
            
            # Unmount any partitions
            import glob
            for part in glob.glob(f"{device}*[0-9]"):
                subprocess.run(['umount', part], capture_output=True, check=False)
        except Exception:
            pass
    
    def _create_partition_table(self, device: str, scheme: str):
        """Create partition table on device."""
        subprocess.run(['parted', '-s', device, 'mklabel', scheme],
                      check=True, capture_output=True)
    
    def _create_partition(self, device: str, fs_type: str, scheme: str):
        """Create a primary partition."""
        # Map filesystem to parted type
        fs_map = {
            'fat32': 'fat32',
            'ntfs': 'ntfs',
            'exfat': 'fat32'  # parted doesn't have exfat type
        }
        
        parted_fs = fs_map.get(fs_type, 'fat32')
        
        # Create partition
        subprocess.run([
            'parted', '-s', device,
            'mkpart', 'primary', parted_fs, '0%', '100%'
        ], check=True, capture_output=True)
        
        # Set appropriate flags
        if scheme == 'mbr':
            subprocess.run(['parted', '-s', device, 'set', '1', 'boot', 'on'],
                          check=True, capture_output=True)
        elif scheme == 'gpt' and fs_type == 'fat32':
            subprocess.run(['parted', '-s', device, 'set', '1', 'esp', 'on'],
                          check=True, capture_output=True)
    
    def _format_partition(self, partition: str, fs_type: str, label: str, quick: bool) -> bool:
        """Format partition with specified filesystem."""
        try:
            if fs_type == 'fat32':
                cmd = ['mkfs.fat', '-F', '32']
                if not quick:
                    cmd.append('-I')
                cmd.extend(['-n', label, partition])
                
            elif fs_type == 'ntfs':
                cmd = ['mkfs.ntfs', '-f'] if quick else ['mkfs.ntfs']
                cmd.extend(['-L', label, partition])
                
            elif fs_type == 'exfat':
                cmd = ['mkfs.exfat', '-n', label, partition]
                
            else:
                print(f"Unsupported filesystem: {fs_type}")
                return False
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Formatting partition failed: {e}")
            return False
    
    def check_filesystem(self, device: str) -> Optional[Dict]:
        """Check filesystem on device."""
        try:
            # Use blkid to get filesystem info
            result = subprocess.run(
                ['blkid', device],
                capture_output=True,
                text=True,
                check=True
            )
            
            info = {}
            for part in result.stdout.strip().split():
                if '=' in part:
                    key, value = part.split('=', 1)
                    info[key.lower()] = value.strip('"')
            
            return info if info else None
            
        except subprocess.CalledProcessError:
            return None
    
    def get_available_filesystems(self) -> list:
        """Get list of available filesystem types."""
        filesystems = ['fat32', 'ntfs']
        
        # Check for exfat support
        try:
            subprocess.run(['which', 'mkfs.exfat'], 
                          capture_output=True, check=False)
            filesystems.append('exfat')
        except:
            pass
        
        return filesystems