"""
Main entry point for MBU-Linux application.
"""

import sys
import traceback
from mbulinux.app import MBULinuxApp

def main():
    """Main function to start the application."""
    try:
        app = MBULinuxApp(sys.argv)
        return app.exec()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())