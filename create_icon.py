#!/usr/bin/env python3
"""
Create a simple icon for MBU-Linux.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create icon directory
os.makedirs("mbulinux/data/icons", exist_ok=True)

# Create 256x256 icon
size = 256
icon = Image.new('RGB', (size, size), color='#0078d7')
draw = ImageDraw.Draw(icon)

# Draw USB symbol
margin = 40
usb_width = size - 2 * margin
usb_height = usb_width // 2

# USB connector
draw.rectangle([margin, margin + usb_height//3, 
                size - margin, margin + 2*usb_height//3], 
               fill='white', outline='white', width=4)

# USB plug
plug_width = usb_width // 6
plug_x = size // 2 - plug_width // 2
draw.rectangle([plug_x, margin, plug_x + plug_width, margin + usb_height//3], 
               fill='white', outline='white', width=2)

# USB pins
pin_height = usb_height // 8
pin_y = margin + usb_height//2 - pin_height//2
draw.rectangle([margin + usb_width//4, pin_y, 
                size - margin - usb_width//4, pin_y + pin_height], 
               fill='#005a9e')

# Save as PNG
icon_path = "mbulinux/data/icons/mbulinux.png"
icon.save(icon_path, "PNG")
print(f"Icon saved to {icon_path}")

# Also create smaller versions for different sizes
for sz in [16, 32, 64, 128]:
    small_icon = icon.resize((sz, sz), Image.Resampling.LANCZOS)
    small_icon.save(f"mbulinux/data/icons/mbulinux_{sz}.png", "PNG")
    print(f"  - {sz}x{sz} icon created")