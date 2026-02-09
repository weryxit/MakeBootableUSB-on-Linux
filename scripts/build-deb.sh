#!/bin/bash
# Build .deb package for MBU-Linux

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
PACKAGE_NAME="mbulinux"
VERSION="0.1.0"

echo "Building MBU-Linux .deb package..."

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Create package structure
PKG_DIR="$BUILD_DIR/$PACKAGE_NAME-$VERSION"
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$PKG_DIR/usr/share/mbulinux"
mkdir -p "$PKG_DIR/usr/share/doc/$PACKAGE_NAME"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --target="$PKG_DIR/usr/share/mbulinux" -r "$PROJECT_DIR/requirements.txt"

# Copy application files
echo "Copying application files..."
cp -r "$PROJECT_DIR/mbulinux" "$PKG_DIR/usr/share/mbulinux/"
cp -r "$PROJECT_DIR/mbulinux/data" "$PKG_DIR/usr/share/mbulinux/"

# Create executable scripts
echo "Creating executables..."

# Main GUI application
cat > "$PKG_DIR/usr/bin/mbulinux" << 'EOF'
#!/bin/bash
python3 -m mbulinux "$@"
EOF
chmod +x "$PKG_DIR/usr/bin/mbulinux"

# CLI application
cat > "$PKG_DIR/usr/bin/mbulinux-cli" << 'EOF'
#!/bin/bash
python3 -m mbulinux.cli "$@"
EOF
chmod +x "$PKG_DIR/usr/bin/mbulinux-cli"

# Create desktop entry
echo "Creating desktop entry..."
cat > "$PKG_DIR/usr/share/applications/mbulinux.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MBU-Linux
GenericName=USB Boot Creator
Comment=Make Bootable USB on Linux
Exec=sudo mbulinux %U
Icon=mbulinux
Terminal=true
Categories=System;Utility;
Keywords=usb;boot;iso;windows;linux;
StartupNotify=true
EOF

# Copy icon (placeholder)
if [ -f "$PROJECT_DIR/mbulinux/data/icons/usb.svg" ]; then
    cp "$PROJECT_DIR/mbulinux/data/icons/usb.svg" \
       "$PKG_DIR/usr/share/icons/hicolor/scalable/apps/mbulinux.svg"
fi

# Create control file
echo "Creating control file..."
cat > "$PKG_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-pip, udisks2, parted, dosfstools, python3-gi, gir1.2-udisks-2.0
Recommends: ntfs-3g, exfatprogs, wimtools, p7zip-full
Maintainer: Your Name <your.email@example.com>
Description: Make Bootable USB on Linux
 A modern GUI tool for creating bootable USB drives from ISO images.
 Supports both Linux and Windows ISO files with advanced features.
Homepage: https://github.com/yourusername/MakeBootableUSB_on_Linux
EOF

# Create post-install script
echo "Creating post-install script..."
cat > "$PKG_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update icon cache
if [ -d /usr/share/icons/hicolor ]; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi

# Update desktop database
update-desktop-database /usr/share/applications || true

echo "MBU-Linux installed successfully!"
echo "Run 'mbulinux' to start the application."
echo "Or 'mbulinux-cli --help' for command-line interface."
EOF
chmod +x "$PKG_DIR/DEBIAN/postinst"

# Create pre-remove script
cat > "$PKG_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e
echo "Removing MBU-Linux..."
EOF
chmod +x "$PKG_DIR/DEBIAN/prerm"

# Create copyright file
echo "Creating copyright file..."
cat > "$PKG_DIR/usr/share/doc/$PACKAGE_NAME/copyright" << 'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: MBU-Linux
Source: https://github.com/yourusername/MakeBootableUSB_on_Linux

Files: *
Copyright: 2024 Your Name <your.email@example.com>
License: GPL-3.0-or-later

License: GPL-3.0-or-later
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.
 .
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.
 .
 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
EOF

# Create changelog
echo "Creating changelog..."
cat > "$PKG_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian" << 'EOF'
mbulinux (0.1.0) unstable; urgency=medium

  * Initial release
  * GUI interface with Qt
  * Support for Linux and Windows ISO
  * UDisks2 integration for safe disk detection

 -- Your Name <your.email@example.com>  $(date -R)
EOF
gzip -9 "$PKG_DIR/usr/share/doc/$PACKAGE_NAME/changelog.Debian"

# Build package
echo "Building package..."
mkdir -p "$DIST_DIR"
dpkg-deb --build "$PKG_DIR" "$DIST_DIR/$PACKAGE_NAME-$VERSION.deb"

echo ""
echo "Package built successfully: $DIST_DIR/$PACKAGE_NAME-$VERSION.deb"
echo ""
echo "To install:"
echo "  sudo dpkg -i $DIST_DIR/$PACKAGE_NAME-$VERSION.deb"
echo "  sudo apt install -f  # Install dependencies"
