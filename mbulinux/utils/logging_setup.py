"""
Logging setup for MBU-Linux.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

from ..constants import CACHE_DIR, LOG_FILE

def setup_logging(level=logging.INFO):
    """
    Setup application logging.
    
    Args:
        level: Logging level
    """
    # Create log directory
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup file handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup
    logger.info("=" * 50)
    logger.info("MBU-Linux started")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info("=" * 50)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_system_info():
    """Log system information."""
    logger = get_logger(__name__)
    
    try:
        import platform
        import psutil
        
        # Basic system info
        logger.info(f"System: {platform.system()} {platform.release()}")
        logger.info(f"Python: {platform.python_version()}")
        logger.info(f"Machine: {platform.machine()}")
        
        # Disk info
        disk_info = []
        for partition in psutil.disk_partitions():
            if 'loop' not in partition.device:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append(
                        f"{partition.device} ({partition.mountpoint}): "
                        f"{usage.percent}% used"
                    )
                except:
                    pass
        
        if disk_info:
            logger.info("Disks: " + ", ".join(disk_info))
        
    except ImportError:
        logger.warning("psutil not available, limited system info")


def cleanup_old_logs(days_to_keep: int = 7):
    """
    Clean up old log files.
    
    Args:
        days_to_keep: Number of days to keep logs
    """
    try:
        log_dir = LOG_FILE.parent
        cutoff_time = datetime.now().timestamp() - (days_to_keep * 86400)
        
        for log_file in log_dir.glob("mbulinux*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                
    except Exception as e:
        get_logger(__name__).warning(f"Failed to cleanup old logs: {e}")