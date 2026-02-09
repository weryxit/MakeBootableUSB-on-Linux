"""
Application constants and configuration.
"""

import os
from pathlib import Path

# Application info
APP_NAME = "MBU-Linux"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Make Bootable USB on Linux"
APP_ORG = "MBU-Linux"
APP_DOMAIN = "mbulinux.org"

# Paths
if "FLATPAK_ID" in os.environ:
    # Flatpak environment
    DATA_DIR = Path("/app/share/mbulinux")
    CONFIG_DIR = Path.home() / ".var" / "app" / "org.mbulinux" / "config"
    CACHE_DIR = Path.home() / ".var" / "app" / "org.mbulinux" / "cache"
else:
    # Standard Linux environment
    DATA_DIR = Path(__file__).parent / "data"
    CONFIG_DIR = Path.home() / ".config" / "mbulinux"
    CACHE_DIR = Path.home() / ".cache" / "mbulinux"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# File paths
SETTINGS_FILE = CONFIG_DIR / "settings.json"
LOG_FILE = CACHE_DIR / "mbulinux.log"

# ISO types
ISO_TYPE_UNKNOWN = 0
ISO_TYPE_LINUX = 1
ISO_TYPE_WINDOWS = 2
ISO_TYPE_MACOS = 3
ISO_TYPE_HYBRID = 4

# Partition schemes
SCHEME_MBR = "mbr"
SCHEME_GPT = "gpt"

# Filesystems
FS_FAT32 = "fat32"
FS_NTFS = "ntfs"
FS_EXFAT = "exfat"

# Default settings
DEFAULT_SETTINGS = {
    "theme": "auto",
    "language": "auto",
    "default_scheme": SCHEME_GPT,
    "default_filesystem": FS_FAT32,
    "validate_after_write": True,
    "eject_after_write": False,
    "check_for_updates": True,
    "window_width": 900,
    "window_height": 700,
}