"""
Base strategy pattern for writing different types of ISOs.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional

class WriteStrategy(ABC):
    """Base class for write strategies."""
    
    def __init__(self):
        self.progress_callback: Optional[Callable[[int, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def update_progress(self, percent: int, message: str):
        """Update progress through callback."""
        if self.progress_callback:
            self.progress_callback(percent, message)
    
    @abstractmethod
    def write(self, iso_path: str, device: str, options: dict) -> bool:
        """
        Write ISO to device.
        
        Args:
            iso_path: Path to ISO file
            device: Block device path (e.g., /dev/sdb)
            options: Additional options (filesystem, scheme, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate(self, iso_path: str, device: str) -> bool:
        """
        Validate the written image.
        
        Args:
            iso_path: Path to original ISO
            device: Block device path
            
        Returns:
            True if validation passed
        """
        pass
    
    @abstractmethod
    def get_required_tools(self) -> list:
        """
        Get list of required command-line tools.
        
        Returns:
            List of required tools
        """
        pass