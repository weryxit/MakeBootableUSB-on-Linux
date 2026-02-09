# MakeBootableUSB-on-Linux

A simple toolset for creating bootable USB drives on Linux systems using scripts and utilities.

## About the Project

MakeBootableUSB-on-Linux is a collection of scripts and utilities designed to help users easily create bootable USB flash drives on Linux systems.

It can be used to write ISO images of operating systems (Linux distributions, recovery tools, installers, etc.) to USB devices.

The main goal of the project is to simplify the process of making bootable USB drives without manually running complex or potentially dangerous commands such as `dd`.

## Features

- Create bootable USB drives from ISO images
- Works on most modern Linux distributions
- Supports BIOS and UEFI boot modes
- Simple and automated workflow
- Reduces the risk of user error during USB formatting and writing

## Repository Contents

This repository may include:

- Shell scripts for creating bootable USB drives
- Python utilities and helper scripts
- Configuration files
- Dependency lists (`requirements.txt`)
- Project metadata (`pyproject.toml`)
- Example or test files

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/weryxit/MakeBootableUSB-on-Linux.git  
   cd MakeBootableUSB-on-Linux
```
2. Install dependencies (if required):
```bash
   python3 -m pip install --user -r requirements.txt
```
3. Set execution permissions for scripts:
```bash
   chmod +x *.sh
```
4. Run the script (requires root privileges):
```bash
   sudo ./install.sh
```
5. Run the application (if you cant from menu):
```bash
   sudo ./run.sh
```
   or
```bash
   ./mbulinux.desktop
```
## Usage

1. Plug in your USB flash drive.
2. Specify the path to the ISO file.
3. Select the correct USB device.
4. The script will format the device and write the bootable image.
5. Wait until the process is completed.

## Warning

All data on the selected USB drive will be permanently erased.  
Make sure you select the correct device before proceeding.

## Requirements

- Linux operating system
- Python 3 (if Python scripts are used)
- Root privileges (sudo)
- Standard Linux utilities (e.g. lsblk, mount, umount)

## Contributing

Contributions are welcome.  
Feel free to open issues for bug reports or feature requests, or submit pull requests.

## License

This project is licensed under the MIT License (or specify another license if applicable).

