"""
Analyze ISO images to detect OS type and properties.
"""

import subprocess
import os
from typing import Dict, Optional
from pathlib import Path

from ..constants import ISO_TYPE_LINUX, ISO_TYPE_WINDOWS, ISO_TYPE_UNKNOWN

class ImageAnalyzer:
    """Analyze ISO images."""
    
    def __init__(self):
        self.signatures = {
            'linux': {
                'files': ['boot/cat', 'boot/grub', 'isolinux/', 'syslinux/', 'casper/'],
                'patterns': [r'LINUX', r'UBUNTU', r'FEDORA', r'DEBIAN', r'ARCH']
            },
            'windows': {
                'files': ['sources/install.wim', 'sources/install.esd', 'bootmgr', 'setup.exe'],
                'patterns': [r'WINDOWS', r'MICROSOFT', r'BOOTMGR']
            }
        }
    
    def analyze(self, iso_path: str) -> Dict:
        """
        Analyze ISO image.
        
        Args:
            iso_path: Path to ISO file
            
        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(iso_path):
            raise FileNotFoundError(f"ISO file not found: {iso_path}")
        
        result = {
            'path': iso_path,
            'size': os.path.getsize(iso_path),
            'type': ISO_TYPE_UNKNOWN,
            'os_name': 'Unknown',
            'architecture': 'Unknown',
            'requires_uefi': False,
            'wim_size': 0,
            'is_hybrid': False,
        }
        
        # Check file extension
        if iso_path.lower().endswith(('.iso', '.img')):
            result['is_hybrid'] = self._check_hybrid(iso_path)
            
            # Try to identify by reading first sector
            try:
                with open(iso_path, 'rb') as f:
                    # Read boot sector
                    f.seek(32768)  # ISO9660 PVD offset
                    data = f.read(2048)
                    
                    # Check for ISO9660/El Torito
                    if b'EL TORITO' in data:
                        result['has_eltorito'] = True
                    
                    # Check for Windows
                    if b'BOOTMGR' in data[:512] or b'NTFS' in data[:512]:
                        result['type'] = ISO_TYPE_WINDOWS
                        result['os_name'] = 'Windows'
                        result['requires_uefi'] = self._check_windows_uefi(iso_path)
                        result['wim_size'] = self._get_wim_size(iso_path)
                    
                    # Check for Linux (GRUB/SYSLINUX)
                    elif b'ISOLINUX' in data or b'GRUB' in data or b'LINUX' in data:
                        result['type'] = ISO_TYPE_LINUX
                        result['os_name'] = self._identify_linux_distro(iso_path)
                        result['architecture'] = self._get_linux_arch(iso_path)
            
            except IOError as e:
                print(f"Error reading ISO: {e}")
        
        return result
    
    def _check_hybrid(self, iso_path: str) -> bool:
        """Check if ISO is hybrid (bootable from CD and USB)."""
        try:
            result = subprocess.run(
                ['file', iso_path],
                capture_output=True,
                text=True,
                check=True
            )
            return 'hybrid' in result.stdout.lower()
        except subprocess.CalledProcessError:
            return False
    
    def _check_windows_uefi(self, iso_path: str) -> bool:
        """Check if Windows ISO requires UEFI."""
        try:
            # Mount ISO temporarily (read-only)
            import tempfile
            import shutil
            
            mount_point = tempfile.mkdtemp()
            try:
                subprocess.run(
                    ['udisksctl', 'loop-setup', '-f', iso_path],
                    check=True,
                    capture_output=True
                )
                
                # Check for EFI directory
                efi_path = os.path.join(mount_point, 'efi')
                result = os.path.exists(efi_path)
                
                # Cleanup
                subprocess.run(['udisksctl', 'loop-delete', '-b', mount_point],
                             capture_output=True)
                
                return result
            finally:
                shutil.rmtree(mount_point, ignore_errors=True)
        except Exception:
            return False
    
    def _get_wim_size(self, iso_path: str) -> int:
        """Get size of Windows WIM file."""
        try:
            # Use 7z to list contents
            result = subprocess.run(
                ['7z', 'l', iso_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if 'install.wim' in line.lower() or 'install.esd' in line.lower():
                    parts = line.split()
                    if len(parts) > 3:
                        try:
                            return int(parts[3])  # Size in bytes
                        except ValueError:
                            pass
        except Exception:
            pass
        
        return 0
    
    def _identify_linux_distro(self, iso_path: str) -> str:
        """Identify Linux distribution."""
        distros = {
            'ubuntu': ['ubuntu', 'kubuntu', 'xubuntu', 'lubuntu'],
            'fedora': ['fedora'],
            'debian': ['debian'],
            'arch': ['arch linux'],
            'manjaro': ['manjaro'],
            'mint': ['linux mint'],
            'opensuse': ['opensuse', 'suse'],
            'centos': ['centos'],
            'rhel': ['red hat'],
        }
        
        try:
            result = subprocess.run(
                ['file', iso_path],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.lower()
            for distro, keywords in distros.items():
                for keyword in keywords:
                    if keyword in output:
                        return distro.capitalize()
        except Exception:
            pass
        
        return 'Linux'
    
    def _get_linux_arch(self, iso_path: str) -> str:
        """Get Linux architecture."""
        try:
            # Check for 64-bit indicators
            with open(iso_path, 'rb') as f:
                f.seek(0x228)  # Architecture identifier offset
                data = f.read(8)
                
                if b'x86_64' in data or b'amd64' in data:
                    return 'x86_64'
                elif b'i386' in data or b'i686' in data:
                    return 'i386'
                elif b'arm64' in data or b'aarch64' in data:
                    return 'arm64'
        except Exception:
            pass
        
        return 'Unknown'