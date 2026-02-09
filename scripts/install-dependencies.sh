#!/bin/bash
# Install dependencies for MBU-Linux

set -e

echo "Installing MBU-Linux dependencies..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Cannot detect distribution"
    exit 1
fi

# Install packages based on distribution
case $DISTRO in
    ubuntu|debian|pop|linuxmint)
        echo "Detected Debian-based distribution"
        apt update
        apt install -y \
            python3-pip \
            python3-venv \
            python3-gi \
            python3-gi-cairo \
            gir1.2-gtk-4.0 \
            gir1.2-udisks-2.0 \
            udisks2 \
            parted \
            dosfstools \
            ntfs-3g \
            exfatprogs \
            wimtools \
            p7zip-full \
            grub-common \
            grub-pc-bin
        ;;
    
    fedora|rhel|centos)
        echo "Detected Red Hat-based distribution"
        dnf install -y \
            python3-pip \
            python3-gobject \
            gtk4 \
            udisks2 \
            udisks2-devel \
            parted \
            dosfstools \
            ntfs-3g \
            exfatprogs \
            wimlib-utils \
            p7zip \
            p7zip-plugins \
            grub2 \
            grub2-tools
        ;;
    
    arch|manjaro)
        echo "Detected Arch-based distribution"
        pacman -Syu --noconfirm \
            python-pip \
            python-gobject \
            gtk4 \
            udisks \
            parted \
            dosfstools \
            ntfs-3g \
            exfatprogs \
            wimlib \
            p7zip \
            grub
        ;;
    
    opensuse*)
        echo "Detected openSUSE distribution"
        zypper install -y \
            python3-pip \
            python3-gobject \
            gtk4 \
            udisks2 \
            parted \
            dosfstools \
            ntfs-3g \
            exfatprogs \
            wimlib \
            p7zip \
            grub2
        ;;
    
    *)
        echo "Unsupported distribution: $DISTRO"
        echo "Please install dependencies manually:"
        echo "- Python 3.10+"
        echo "- PySide6"
        echo "- udisks2"
        echo "- parted"
        echo "- dosfstools"
        echo "- ntfs-3g (optional)"
        echo "- exfatprogs (optional)"
        echo "- wimtools (optional, for Windows)"
        echo "- p7zip (optional)"
        exit 1
        ;;
esac

echo ""
echo "Dependencies installed successfully!"
echo ""
echo "For Python packages, run:"
echo "  pip install -r requirements.txt"