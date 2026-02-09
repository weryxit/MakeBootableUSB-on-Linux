"""
Writer strategies for different OS types.
"""

from .base_strategy import WriteStrategy
from .linux_strategy import LinuxWriteStrategy
from .windows_strategy import WindowsWriteStrategy

__all__ = [
    'WriteStrategy',
    'LinuxWriteStrategy',
    'WindowsWriteStrategy'
]