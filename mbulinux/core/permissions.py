"""
Handle permissions and privilege escalation.
"""

import subprocess
import os
import sys
from typing import Optional

class PermissionManager:
    """Manage permissions for disk operations."""
    
    def __init__(self):
        self.use_polkit = self._check_polkit()
        self.use_sudo = self._check_sudo()
    
    def _check_polkit(self) -> bool:
        """Check if polkit is available."""
        try:
            subprocess.run(['pkexec', '--version'],
                          capture_output=True, check=False)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_sudo(self) -> bool:
        """Check if sudo is available."""
        try:
            subprocess.run(['sudo', '--version'],
                          capture_output=True, check=False)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_root(self) -> bool:
        """Check if running as root."""
        return os.geteuid() == 0
    
    def get_permission_command(self, command: list) -> list:
        """
        Wrap command with appropriate privilege escalation.
        
        Args:
            command: List of command arguments
            
        Returns:
            Command wrapped with sudo/pkexec if needed
        """
        if self.check_root():
            return command
        
        if self.use_polkit:
            return ['pkexec'] + command
        elif self.use_sudo:
            return ['sudo'] + command
        else:
            # Try to run without escalation (might fail)
            return command
    
    def run_with_permissions(self, command: list, **kwargs) -> subprocess.CompletedProcess:
        """
        Run command with appropriate permissions.
        
        Args:
            command: Command to run
            **kwargs: Additional arguments for subprocess.run
            
        Returns:
            CompletedProcess object
        """
        wrapped_cmd = self.get_permission_command(command)
        
        try:
            return subprocess.run(
                wrapped_cmd,
                **kwargs
            )
        except subprocess.CalledProcessError as e:
            raise PermissionError(f"Command failed with permissions: {e}")
    
    def request_permissions(self, message: str = "Authentication required") -> bool:
        """
        Request permissions from user.
        
        Args:
            message: Message to display to user
            
        Returns:
            True if permissions granted
        """
        if self.check_root():
            return True
        
        # Try polkit first
        if self.use_polkit:
            try:
                # Test with a simple command
                result = subprocess.run(
                    ['pkexec', 'echo', 'test'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.returncode == 0
            except:
                pass
        
        # Try sudo
        if self.use_sudo:
            try:
                result = subprocess.run(
                    ['sudo', '-v'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                return result.returncode == 0
            except:
                pass
        
        return False
    
    def create_desktop_entry(self) -> bool:
        """Create desktop entry with elevated privileges."""
        desktop_content = """[Desktop Entry]
            Version=1.0
            Type=Application
            Name=MBU-Linux
            Comment=Make Bootable USB on Linux
            Exec={exec_path} %U
            Icon=mbulinux
            Terminal=false
            Categories=System;Utility;
            """
        
        # Get current executable path
        exec_path = sys.executable if hasattr(sys, '_MEIPASS') else sys.argv[0]
        
        desktop_file = os.path.expanduser('~/.local/share/applications/mbulinux.desktop')
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(desktop_file), exist_ok=True)
            
            # Write desktop file
            with open(desktop_file, 'w') as f:
                f.write(desktop_content.format(exec_path=exec_path))
            
            # Make executable
            os.chmod(desktop_file, 0o755)
            
            # Update desktop database
            subprocess.run(['update-desktop-database',
                          os.path.expanduser('~/.local/share/applications')],
                          check=False)
            
            return True
        except Exception as e:
            print(f"Failed to create desktop entry: {e}")
            return False