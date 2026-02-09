#!/bin/bash
# Installation script for MBU-Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing MBU-Linux from: $(pwd)"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Installing system-wide..."
    INSTALL_PREFIX="/usr"
    PIP_USER=""
else
    echo "Installing for current user..."
    INSTALL_PREFIX="$HOME/.local"
    PIP_USER="--user"
fi

# Install Python package
echo "Installing Python package..."
pip install $PIP_USER -e . --break-system-packages

# Create necessary directories
mkdir -p "$INSTALL_PREFIX/share/applications"
mkdir -p "$INSTALL_PREFIX/share/icons/hicolor/scalable/apps"

# Install .desktop file
echo "Installing desktop file..."
if [ -f "mbulinux.desktop" ]; then
    cp "mbulinux.desktop" "$INSTALL_PREFIX/share/applications/"
    echo "✓ Desktop file installed"
else
    echo "✗ Desktop file not found"
fi

# Install icon
echo "Installing icon..."
if [ -f "mbulinux/data/icons/mbulinux.svg" ]; then
    cp "mbulinux/data/icons/mbulinux.svg" "$INSTALL_PREFIX/share/icons/hicolor/scalable/apps/"
    echo "✓ Icon installed"
else
    # Create simple icon if missing
    echo "⚠ Icon not found, creating simple one..."
    cat > "/tmp/mbulinux.svg" << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">
  <rect width="256" height="256" rx="40" fill="#0078d7"/>
  <rect x="80" y="100" width="96" height="56" fill="white" rx="8"/>
  <rect x="128" y="80" width="16" height="20" fill="white"/>
  <rect x="100" y="128" width="56" height="16" fill="#005a9e"/>
  <text x="128" y="220" text-anchor="middle" font-family="Arial" 
        font-size="24" fill="white">MBU</text>
</svg>
EOF
    cp "/tmp/mbulinux.svg" "$INSTALL_PREFIX/share/icons/hicolor/scalable/apps/mbulinux.svg"
    echo "✓ Simple icon created"
fi

# Update icon cache (if gtk-update-icon-cache exists)
if command -v gtk-update-icon-cache &> /dev/null && [ -d "$INSTALL_PREFIX/share/icons/hicolor" ]; then
    echo "Updating icon cache..."
    gtk-update-icon-cache -f -t "$INSTALL_PREFIX/share/icons/hicolor" || true
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    echo "Updating desktop database..."
    update-desktop-database "$INSTALL_PREFIX/share/applications" || true
fi

echo Install completed succefully. Run mbulinux from terminal or Desktop