"""
System information and dependency checking.
"""

import subprocess
import sys
import platform
from typing import List, Dict, Optional

def check_dependencies() -> Dict[str, bool]:
    """
    Check for required system dependencies.
    
    Returns:
        Dictionary of tool: available
    """
    dependencies = {
        'dd': 'Disk duplication',
        'parted': 'Partition editing',
        'mkfs.fat': 'FAT filesystem creation',
        'mkfs.ntfs': 'NTFS filesystem creation (optional)',
        'mkfs.exfat': 'exFAT filesystem creation (optional)',
        'wimlib-imagex': 'Windows WIM handling (optional)',
        '7z': 'Archive extraction (optional)',
        'udisksctl': 'Disk management',
        'pkexec': 'Privilege escalation (optional)',
        'sudo': 'Privilege escalation (optional)',
    }
    
    results = {}
    
    for tool, description in dependencies.items():
        try:
            if tool == 'mkfs.fat':
                # Check for mkfs.fat or mkfs.vfat
                result1 = subprocess.run(['which', 'mkfs.fat'], 
                                       capture_output=True, check=False)
                result2 = subprocess.run(['which', 'mkfs.vfat'],
                                       capture_output=True, check=False)
                available = result1.returncode == 0 or result2.returncode == 0
            elif tool == 'mkfs.ntfs':
                # Check for mkfs.ntfs or mkntfs
                result1 = subprocess.run(['which', 'mkfs.ntfs'],
                                       capture_output=True, check=False)
                result2 = subprocess.run(['which', 'mkntfs'],
                                       capture_output=True, check=False)
                available = result1.returncode == 0 or result2.returncode == 0
            else:
                result = subprocess.run(['which', tool],
                                      capture_output=True, check=False)
                available = result.returncode == 0
            
            results[tool] = available
            
            if not available and 'optional' not in description:
                print(f"Warning: Required tool '{tool}' not found")
                
        except Exception:
            results[tool] = False
    
    return results


def get_system_info() -> Dict:
    """
    Get system information.
    
    Returns:
        Dictionary with system info
    """
    info = {}
    
    try:
        import platform
        import psutil
        
        # Basic info
        info['system'] = platform.system()
        info['release'] = platform.release()
        info['version'] = platform.version()
        info['machine'] = platform.machine()
        info['processor'] = platform.processor()
        
        # Python info
        info['python_version'] = platform.python_version()
        info['python_implementation'] = platform.python_implementation()
        
        # CPU info
        info['cpu_count'] = psutil.cpu_count()
        info['cpu_freq'] = psutil.cpu_freq().current if psutil.cpu_freq() else None
        
        # Memory info
        mem = psutil.virtual_memory()
        info['memory_total'] = mem.total
        info['memory_available'] = mem.available
        
        # Disk info
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                })
            except:
                pass
        info['disks'] = disks
        
    except ImportError as e:
        info['error'] = f"Failed to get system info: {e}"
    
    return info


def is_uefi_boot() -> bool:
    """
    Check if system is booted in UEFI mode.
    
    Returns:
        True if UEFI boot
    """
    try:
        # Check for efivars directory
        import os
        if os.path.exists('/sys/firmware/efi'):
            return True
        
        # Check boot entry
        result = subprocess.run(['bootctl', 'status'],
                              capture_output=True, text=True, check=False)
        if result.returncode == 0 and 'Boot loader spec not found' not in result.stdout:
            return 'EFI' in result.stdout
        
        return False
        
    except Exception:
        return False


def get_available_disks() -> List[Dict]:
    """
    Get available disks using lsblk.
    
    Returns:
        List of disk information
    """
    try:
        result = subprocess.run(
            ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MODEL,VENDOR,RO,MOUNTPOINT,PKNAME'],
            capture_output=True,
            text=True,
            check=True
        )
        
        import json
        data = json.loads(result.stdout)
        
        disks = []
        for device in data.get('blockdevices', []):
            if device.get('type') == 'disk' and device.get('pkname') is None:
                disks.append({
                    'name': device['name'],
                    'size': device.get('size', '0'),
                    'model': device.get('model', ''),
                    'vendor': device.get('vendor', ''),
                    'read_only': device.get('ro', '0') == '1',
                    'mountpoint': device.get('mountpoint'),
                })
        
        return disks
        
    except Exception as e:
        print(f"Error getting disks: {e}")
        return []