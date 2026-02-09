#!/usr/bin/env python3
"""
Setup script for MBU-Linux.
"""

from setuptools import setup, find_packages
import os

# Get long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mbulinux",
    version="0.1.0",
    description="Make Bootable USB on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="weryxit",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/MakeBootableUSB_on_Linux",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'mbulinux': ['data/icons/*', 'data/styles/*', 'data/schemas/*'],
    },
    data_files=[
        ('share/applications', ['mbulinux.desktop']),
        ('share/icons/hicolor/scalable/apps', ['mbulinux/data/icons/mbulinux.svg']),
        ('share/icons/hicolor/256x256/apps', ['mbulinux/data/icons/mbulinux.png']),
        ('share/icons/hicolor/128x128/apps', ['mbulinux/data/icons/mbulinux_128.png']),
        ('share/icons/hicolor/64x64/apps', ['mbulinux/data/icons/mbulinux_64.png']),
        ('share/icons/hicolor/32x32/apps', ['mbulinux/data/icons/mbulinux_32.png']),
        ('share/icons/hicolor/16x16/apps', ['mbulinux/data/icons/mbulinux_16.png']),
    ],
    install_requires=[
        "PySide6>=6.5.0",
        "pydbus>=0.6.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "mbulinux=mbulinux.__main__:main",
            "mbulinux-cli=mbulinux.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Installation",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)