"""
Strategy for writing Windows ISO images.
"""

import subprocess
import os
import tempfile
import shutil
from typing import Optional
from pathlib import Path

from .base_strategy import WriteStrategy

class WindowsWriteStrategy(WriteStrategy):
    """Write strategy for Windows ISO images."""
    
    def __init__(self):
        super().__init__()
    
    def get_required_tools(self) -> list:
        tools = ['parted', 'mkfs.fat', 'mkfs.ntfs', 'wimlib-imagex']
        
        # Check for wimlib
        try:
            subprocess.run(['wimlib-imagex', '--version'], 
                          capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            tools.remove('wimlib-imagex')
            tools.append('7z')  # Fallback to 7z
        
        return tools
    
    def write(self, iso_path: str, device: str, options: dict) -> bool:
        """
        Write Windows ISO with proper handling of large WIM files.
        
        Args:
            iso_path: Path to Windows ISO
            device: Block device path
            options: Writing options
            
        Returns:
            True if successful
        """
        self.update_progress(0, "Preparing Windows ISO...")
        
        # Analyze ISO
        from ...core.image_analyzer import ImageAnalyzer
        analyzer = ImageAnalyzer()
        iso_info = analyzer.analyze(iso_path)
        
        # Check WIM size
        wim_size = iso_info.get('wim_size', 0)
        needs_split = wim_size > 4 * 1024**3  # > 4GB
        
        # Unmount device
        self._unmount_device(device)
        
        # Format device
        if not self._format_for_windows(device, options, needs_split):
            return False
        
        # Extract ISO
        return self._extract_and_copy(iso_path, device, needs_split)
    
    def validate(self, iso_path: str, device: str) -> bool:
        """Validate Windows installation."""
        # For Windows, check if boot files exist
        try:
            # Mount device partition
            import tempfile
            mount_point = tempfile.mkdtemp()
            
            partition = f"{device}1"
            subprocess.run(['mount', partition, mount_point], 
                          capture_output=True, check=True)
            
            # Check for essential Windows files
            essential_files = ['bootmgr', 'boot/BCD', 'sources/boot.wim']
            all_exist = all(
                os.path.exists(os.path.join(mount_point, f))
                for f in essential_files
            )
            
            # Unmount
            subprocess.run(['umount', mount_point], check=True)
            shutil.rmtree(mount_point)
            
            return all_exist
        except Exception:
            return False
    
    def _format_for_windows(self, device: str, options: dict, needs_split: bool) -> bool:
        """Format device for Windows installation."""
        try:
            scheme = options.get('scheme', 'gpt')
            
            # For UEFI, GPT is required
            if options.get('uefi', True) and scheme != 'gpt':
                self.update_progress(0, "UEFI requires GPT partition scheme")
                scheme = 'gpt'
            
            self.update_progress(5, f"Creating {scheme.upper()} partition table...")
            
            # Create partition table
            subprocess.run(['parted', '-s', device, 'mklabel', scheme],
                          check=True, capture_output=True)
            
            # Create partitions
            if needs_split:
                # FAT32 (boot) + NTFS (install) for large WIM
                self._create_dual_partitions(device)
            else:
                # Single NTFS partition
                self._create_single_partition(device, scheme)
            
            self.update_progress(10, "Formatting completed")
            return True
            
        except subprocess.CalledProcessError as e:
            self.update_progress(0, f"Formatting failed: {e}")
            return False
    
    def _create_single_partition(self, device: str, scheme: str):
        """Create single NTFS partition."""
        # Create NTFS partition
        subprocess.run(['parted', '-s', device, 'mkpart', 'primary', 'ntfs', '0%', '100%'],
                      check=True)
        
        # Set boot/esp flags
        partition = f"{device}1"
        if scheme == 'gpt':
            subprocess.run(['parted', '-s', device, 'set', '1', 'esp', 'on'],
                          check=True)
        else:
            subprocess.run(['parted', '-s', device, 'set', '1', 'boot', 'on'],
                          check=True)
        
        # Format as NTFS
        subprocess.run(['mkfs.ntfs', '-f', '-L', 'WININSTALL', partition],
                      check=True)
    
    def _create_dual_partitions(self, device: str):
        """Create FAT32 (boot) + NTFS (install) partitions."""
        # FAT32 partition for boot (1GB)
        subprocess.run(['parted', '-s', device, 'mkpart', 'primary', 'fat32', '0%', '1GB'],
                      check=True)
        subprocess.run(['parted', '-s', device, 'set', '1', 'esp', 'on'],
                      check=True)
        subprocess.run(['mkfs.fat', '-F', '32', '-n', 'BOOT', f"{device}1"],
                      check=True)
        
        # NTFS partition for install (rest of space)
        subprocess.run(['parted', '-s', device, 'mkpart', 'primary', 'ntfs', '1GB', '100%'],
                      check=True)
        subprocess.run(['mkfs.ntfs', '-f', '-L', 'WINDOWS', f"{device}2"],
                      check=True)
    
    def _extract_and_copy(self, iso_path: str, device: str, needs_split: bool) -> bool:
        """Extract ISO and copy files to device."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            self.update_progress(15, "Extracting ISO files...")
            
            # Extract ISO using 7z
            subprocess.run(['7z', 'x', iso_path, f'-o{temp_dir}'],
                          check=True, capture_output=True)
            
            # Handle WIM splitting if needed
            if needs_split:
                wim_path = os.path.join(temp_dir, 'sources', 'install.wim')
                if os.path.exists(wim_path):
                    self.update_progress(30, "Splitting large WIM file...")
                    self._split_wim_file(wim_path)
            
            # Copy files to device
            if needs_split:
                # Copy boot files to FAT32 partition
                self.update_progress(50, "Copying boot files...")
                self._copy_boot_files(temp_dir, f"{device}1")
                
                # Copy install files to NTFS partition
                self.update_progress(70, "Copying installation files...")
                self._copy_install_files(temp_dir, f"{device}2")
            else:
                # Copy all files to single partition
                self.update_progress(60, "Copying files to USB...")
                self._copy_all_files(temp_dir, f"{device}1")
            
            self.update_progress(95, "Finalizing...")
            
            # Install bootloader
            self._install_bootloader(device, needs_split)
            
            # Sync
            subprocess.run(['sync'], check=True)
            
            self.update_progress(100, "Windows USB created successfully!")
            return True
            
        except Exception as e:
            self.update_progress(0, f"Error: {e}")
            return False
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _split_wim_file(self, wim_path: str):
        """Split WIM file if it's larger than 4GB."""
        try:
            # Use wimlib to split
            base_name = os.path.splitext(wim_path)[0]
            subprocess.run([
                'wimlib-imagex', 'split',
                wim_path,
                f"{base_name}.swm",
                '3800'  # Split at 3.8GB to be safe
            ], check=True)
            
            # Remove original WIM
            os.remove(wim_path)
        except Exception:
            # Fallback method
            pass
    
    def _copy_boot_files(self, source_dir: str, partition: str):
        """Copy boot files to FAT32 partition."""
        mount_point = tempfile.mkdtemp()
        try:
            # Mount FAT32 partition
            subprocess.run(['mount', partition, mount_point], check=True)
            
            # Copy essential boot files
            boot_files = ['bootmgr', 'boot/', 'efi/', 'sources/boot.wim']
            for item in boot_files:
                src = os.path.join(source_dir, item)
                dst = os.path.join(mount_point, item)
                
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                elif os.path.exists(src):
                    shutil.copy2(src, dst)
            
            # Unmount
            subprocess.run(['umount', mount_point], check=True)
        finally:
            shutil.rmtree(mount_point, ignore_errors=True)
    
    def _copy_install_files(self, source_dir: str, partition: str):
        """Copy installation files to NTFS partition."""
        mount_point = tempfile.mkdtemp()
        try:
            # Mount NTFS partition
            subprocess.run(['mount', partition, mount_point], check=True)
            
            # Copy everything except boot files already copied
            for item in os.listdir(source_dir):
                if item not in ['bootmgr', 'boot', 'efi']:
                    src = os.path.join(source_dir, item)
                    dst = os.path.join(mount_point, item)
                    
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            
            # Unmount
            subprocess.run(['umount', mount_point], check=True)
        finally:
            shutil.rmtree(mount_point, ignore_errors=True)
    
    def _copy_all_files(self, source_dir: str, partition: str):
        """Copy all files to single partition."""
        mount_point = tempfile.mkdtemp()
        try:
            # Mount partition
            subprocess.run(['mount', partition, mount_point], check=True)
            
            # Copy everything
            shutil.copytree(source_dir, mount_point, dirs_exist_ok=True)
            
            # Unmount
            subprocess.run(['umount', mount_point], check=True)
        finally:
            shutil.rmtree(mount_point, ignore_errors=True)
    
    def _install_bootloader(self, device: str, dual_partition: bool):
        """Install bootloader."""
        try:
            if dual_partition:
                # Install GRUB for dual-boot setup
                boot_partition = f"{device}1"
                self._install_grub(boot_partition)
            else:
                # Use Windows bootmgr directly
                pass
        except Exception:
            pass
    
    def _install_grub(self, partition: str):
        """Install GRUB bootloader."""
        mount_point = tempfile.mkdtemp()
        try:
            subprocess.run(['mount', partition, mount_point], check=True)
            
            # Create GRUB directory
            grub_dir = os.path.join(mount_point, 'boot/grub')
            os.makedirs(grub_dir, exist_ok=True)
            
            # Create simple GRUB config
            grub_cfg = os.path.join(grub_dir, 'grub.cfg')
            with open(grub_cfg, 'w') as f:
                f.write("""
menuentry "Install Windows" {
    chainloader /bootmgr
}
""")
            
            # Install GRUB
            subprocess.run([
                'grub-install',
                '--target=i386-pc',
                f'--boot-directory={mount_point}/boot',
                partition
            ], capture_output=True, check=False)
            
            subprocess.run(['umount', mount_point], check=True)
        finally:
            shutil.rmtree(mount_point, ignore_errors=True)
