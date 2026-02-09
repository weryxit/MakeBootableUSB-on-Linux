#!/usr/bin/env python3
"""
Command-line interface for MBU-Linux.
"""

import argparse
import sys
import os
from pathlib import Path

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Make Bootable USB on Linux - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --iso ubuntu.iso --device /dev/sdb
  %(prog)s --iso windows.iso --device /dev/sdc --scheme gpt --fs ntfs
  %(prog)s --list-devices
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--iso',
        help='Path to ISO image file'
    )
    
    parser.add_argument(
        '--device',
        help='Target device (e.g., /dev/sdb)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--scheme',
        choices=['mbr', 'gpt'],
        default='gpt',
        help='Partition scheme (default: gpt)'
    )
    
    parser.add_argument(
        '--fs',
        choices=['fat32', 'ntfs', 'exfat'],
        default='fat32',
        help='Filesystem type (default: fat32)'
    )
    
    parser.add_argument(
        '--label',
        default='BOOTUSB',
        help='Volume label (default: BOOTUSB)'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Use quick format'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Skip validation after write'
    )
    
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available USB devices'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.version:
        from mbulinux import __version__
        print(f"MBU-Linux CLI v{__version__}")
        return 0
    
    if args.list_devices:
        list_devices()
        return 0
    
    # Check required arguments
    if not args.iso and not args.list_devices:
        parser.error("--iso is required unless using --list-devices")
    
    if args.iso and not args.device:
        parser.error("--device is required when using --iso")
    
    # Validate inputs
    if args.iso and not os.path.exists(args.iso):
        print(f"Error: ISO file not found: {args.iso}", file=sys.stderr)
        return 1
    
    if args.device and not os.path.exists(args.device):
        print(f"Error: Device not found: {args.device}", file=sys.stderr)
        return 1
    
    # Run the write operation
    return run_write(args)

def list_devices():
    """List available USB devices."""
    try:
        from mbulinux.core.disk_manager import DiskManager
        
        manager = DiskManager()
        disks = manager.get_removable_disks()
        
        if not disks:
            print("No USB devices found.")
            return
        
        print(f"Found {len(disks)} USB device(s):")
        print("-" * 60)
        
        for i, disk in enumerate(disks, 1):
            print(f"{i}. {disk['model']} ({disk['vendor']})")
            print(f"   Device: {disk['device']}")
            print(f"   Size: {disk['size_gb']:.1f} GB")
            
            if disk.get('read_only'):
                print("   Status: Read-only")
            
            if disk.get('mount_points'):
                print(f"   Mounted at: {', '.join(disk['mount_points'])}")
            
            print()
            
    except Exception as e:
        print(f"Error listing devices: {e}", file=sys.stderr)

def run_write(args) -> int:
    """Run write operation from CLI."""
    try:
        print(f"MBU-Linux - Creating bootable USB")
        print(f"ISO: {args.iso}")
        print(f"Device: {args.device}")
        print(f"Scheme: {args.scheme.upper()}")
        print(f"Filesystem: {args.fs.upper()}")
        print("-" * 40)
        
        # Import here to avoid GUI dependencies
        from mbulinux.core.image_analyzer import ImageAnalyzer
        from mbulinux.core.permissions import PermissionManager
        
        # Check permissions
        perm_manager = PermissionManager()
        if not perm_manager.request_permissions():
            print("Error: Insufficient permissions. Run with sudo.", file=sys.stderr)
            return 1
        
        # Analyze ISO
        analyzer = ImageAnalyzer()
        iso_info = analyzer.analyze(args.iso)
        
        print(f"OS: {iso_info['os_name']}")
        print(f"Architecture: {iso_info['architecture']}")
        
        if iso_info.get('wim_size', 0) > 4 * 1024**3:
            print("Note: Large WIM file detected, will use NTFS")
            args.fs = 'ntfs'
        
        # Get appropriate strategy
        iso_type = iso_info.get('type')
        
        if iso_type == 2:  # Windows
            from mbulinux.core.writer_strategies.windows_strategy import WindowsWriteStrategy
            strategy = WindowsWriteStrategy()
        else:  # Linux and others
            from mbulinux.core.writer_strategies.linux_strategy import LinuxWriteStrategy
            strategy = LinuxWriteStrategy()
        
        # Setup progress callback
        def progress_callback(percent, message):
            print(f"\r[{percent:3d}%] {message}", end='', flush=True)
        
        strategy.set_progress_callback(progress_callback)
        
        # Prepare options
        options = {
            'scheme': args.scheme,
            'filesystem': args.fs,
            'label': args.label,
            'quick': args.quick,
            'validate': not args.no_validate,
        }
        
        # Confirm
        print(f"\nWARNING: This will ERASE ALL DATA on {args.device}!")
        response = input("Type 'YES' to continue: ")
        
        if response.upper() != 'YES':
            print("Operation cancelled.")
            return 0
        
        # Perform write
        print("\nStarting write operation...")
        success = strategy.write(args.iso, args.device, options)
        
        if success:
            print(f"\n\nSuccess! Bootable USB created on {args.device}")
            return 0
        else:
            print(f"\n\nError: Failed to create bootable USB", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\n\nError: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())