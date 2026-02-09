"""
Strategy for writing Linux ISO images.
"""

import subprocess
import time
import os
from typing import Optional
from .base_strategy import WriteStrategy

class LinuxWriteStrategy(WriteStrategy):
    """Write strategy for Linux ISO images (using dd)."""
    
    def __init__(self):
        super().__init__()
        self.block_size = 4 * 1024 * 1024  # 4MB blocks for better performance
    
    def get_required_tools(self) -> list:
        return ['dd', 'sync', 'parted']
    
    def write(self, iso_path: str, device: str, options: dict) -> bool:
        """
        Write Linux ISO using dd.
        
        Args:
            iso_path: Path to ISO file
            device: Block device path
            options: {'filesystem': 'fat32', 'scheme': 'gpt', ...}
            
        Returns:
            True if successful
        """
        self.update_progress(0, "Starting Linux ISO write...")
        
        # Check if device exists
        if not os.path.exists(device):
            self.update_progress(0, f"Device {device} not found")
            return False
        
        # Unmount device if mounted
        self._unmount_device(device)
        
        # Get ISO size
        iso_size = os.path.getsize(iso_path)
        
        # Format if requested
        if options.get('format', True):
            if not self._format_device(device, options):
                return False
        
        # Write ISO with dd
        try:
            self.update_progress(5, f"Writing {iso_path} to {device}...")
            
            # Calculate optimal block size
            block_size = self._get_optimal_block_size(device)
            
            # Start dd process
            cmd = [
                'dd',
                f'if={iso_path}',
                f'of={device}',
                f'bs={block_size}',
                'status=progress',
                'conv=fsync',
                'oflag=direct'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress
            for line in process.stdout:
                if 'bytes' in line:
                    # Parse dd output for progress
                    try:
                        # Format: "12345678 bytes (12 MB, 11 MiB) copied, 1.2345 s, 10.0 MB/s"
                        parts = line.split()
                        if len(parts) >= 1:
                            bytes_written = int(parts[0])
                            percent = min(99, int((bytes_written / iso_size) * 100))
                            speed = parts[-2] if len(parts) >= 3 else "N/A"
                            self.update_progress(percent, f"Writing: {percent}% ({speed})")
                    except (ValueError, IndexError):
                        pass
            
            # Wait for completion
            process.wait()
            
            if process.returncode == 0:
                self.update_progress(100, "Write completed successfully")
                
                # Sync to ensure all data is written
                subprocess.run(['sync'], check=False)
                return True
            else:
                self.update_progress(0, f"dd failed with code {process.returncode}")
                return False
                
        except subprocess.CalledProcessError as e:
            self.update_progress(0, f"Error during write: {e}")
            return False
        except Exception as e:
            self.update_progress(0, f"Unexpected error: {e}")
            return False
    
    def validate(self, iso_path: str, device: str) -> bool:
        """Simple validation by checking first few bytes."""
        try:
            # Read first 512 bytes from ISO
            with open(iso_path, 'rb') as f:
                iso_data = f.read(512)
            
            # Read first 512 bytes from device
            with open(device, 'rb') as f:
                device_data = f.read(512)
            
            return iso_data == device_data
        except Exception:
            return False
    
    def _unmount_device(self, device: str):
        """Unmount device and all its partitions."""
        try:
            # Unmount using udisksctl
            subprocess.run(['udisksctl', 'unmount', '-b', device],
                          capture_output=True, check=False)
            
            # Also try to unmount any partitions
            import glob
            for part in glob.glob(f"{device}*[0-9]"):
                subprocess.run(['udisksctl', 'unmount', '-b', part],
                              capture_output=True, check=False)
        except Exception:
            pass
    
    def _format_device(self, device: str, options: dict) -> bool:
        """Format device with selected options."""
        try:
            scheme = options.get('scheme', 'gpt')
            fs = options.get('filesystem', 'fat32')
            
            self.update_progress(0, f"Formatting {device} as {fs} ({scheme})...")
            
            # Create partition table
            subprocess.run(['parted', '-s', device, 'mklabel', scheme],
                          check=True, capture_output=True)
            
            # Create single partition
            subprocess.run(['parted', '-s', device, 'mkpart', 'primary', fs, '0%', '100%'],
                          check=True, capture_output=True)
            
            # Set boot flag for MBR
            if scheme == 'mbr':
                subprocess.run(['parted', '-s', device, 'set', '1', 'boot', 'on'],
                              check=True, capture_output=True)
            
            # Format partition
            partition = f"{device}1"
            time.sleep(1)  # Wait for partition to appear
            
            if fs == 'fat32':
                subprocess.run(['mkfs.fat', '-F', '32', '-n', 'BOOTUSB', partition],
                              check=True, capture_output=True)
            elif fs == 'ntfs':
                subprocess.run(['mkfs.ntfs', '-f', '-L', 'BOOTUSB', partition],
                              check=True, capture_output=True)
            elif fs == 'exfat':
                subprocess.run(['mkfs.exfat', '-n', 'BOOTUSB', partition],
                              check=True, capture_output=True)
            
            self.update_progress(2, "Formatting completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.update_progress(0, f"Formatting failed: {e}")
            return False
    
    def _get_optimal_block_size(self, device: str) -> str:
        """Get optimal block size for device."""
        try:
            # Try to get optimal I/O size
            with open(f"/sys/block/{device.split('/')[-1]}/queue/optimal_io_size", 'r') as f:
                optimal = f.read().strip()
                if optimal and optimal != '0':
                    return f"{int(optimal) // 1024}K"
        except:
            pass
        
        return "4M"  # Default
