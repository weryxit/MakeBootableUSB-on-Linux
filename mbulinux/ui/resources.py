"""
Resource management for UI.
"""

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtGui import QIcon, QPixmap
from pathlib import Path

from ..constants import DATA_DIR

def load_style(theme: str = "light") -> str:
    """
    Load QSS style from file.
    
    Args:
        theme: Theme name (light, dark, auto)
        
    Returns:
        QSS style string
    """
    style_file = DATA_DIR / "styles" / f"{theme}.qss"
    
    if style_file.exists():
        with open(style_file, 'r') as f:
            return f.read()
    
    # Default style
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }
    
    QPushButton {
        background-color: #0078d7;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    QPushButton:hover {
        background-color: #106ebe;
    }
    
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    
    QLabel {
        color: #333333;
    }
    
    QProgressBar {
        border: 1px solid #cccccc;
        border-radius: 3px;
        text-align: center;
    }
    
    QProgressBar::chunk {
        background-color: #0078d7;
        border-radius: 3px;
    }
    """

def get_icon(name: str) -> QIcon:
    """
    Get icon by name.
    
    Args:
        name: Icon name without extension
        
    Returns:
        QIcon object
    """
    icon_path = DATA_DIR / "icons" / f"{name}.svg"
    
    if icon_path.exists():
        return QIcon(str(icon_path))
    
    # Fallback to PNG
    icon_path = DATA_DIR / "icons" / f"{name}.png"
    if icon_path.exists():
        return QIcon(str(icon_path))
    
    # Return empty icon if not found
    return QIcon()

def get_pixmap(name: str, size: tuple = (64, 64)) -> QPixmap:
    """
    Get pixmap by name.
    
    Args:
        name: Image name without extension
        size: Desired size (width, height)
        
    Returns:
        QPixmap object
    """
    image_path = DATA_DIR / "icons" / f"{name}.png"
    
    if image_path.exists():
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            return pixmap.scaled(*size)
    
    # Return empty pixmap if not found
    return QPixmap(*size)