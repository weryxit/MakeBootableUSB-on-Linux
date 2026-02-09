"""
Main application class.
"""

import json
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QLocale, QTranslator
from PySide6.QtGui import QIcon, QFontDatabase

from .constants import APP_NAME, APP_ORG, CONFIG_DIR, SETTINGS_FILE, DATA_DIR
from .ui.main_window import MainWindow

class MBULinuxApp(QApplication):
    """Main application class."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Application metadata
        self.setApplicationName(APP_NAME)
        self.setOrganizationName(APP_ORG)
        self.setApplicationVersion("0.1.0")
        
        # Load settings
        self.settings = self.load_settings()
        
        # Setup internationalization
        self.setup_translations()
        
        # Load fonts
        self.load_fonts()
        
        # Apply style
        self.apply_style()
        
        # Create main window
        self.main_window = MainWindow(self.settings)
        self.main_window.show()
    
    def load_settings(self):
        """Load application settings from file."""
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                settings = {}
        else:
            settings = {}
        
        # Merge with defaults
        from .constants import DEFAULT_SETTINGS
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        
        return settings
    
    def save_settings(self):
        """Save application settings to file."""
        # Update from main window if it exists
        if hasattr(self, 'main_window'):
            self.settings.update(self.main_window.get_current_settings())
        
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Failed to save settings: {e}", file=sys.stderr)
    
    def setup_translations(self):
        """Setup application translations."""
        locale = QLocale.system().name()
        
        # Load Qt translations
        qt_translator = QTranslator()
        if qt_translator.load(f"qt_{locale}", ":/i18n/"):
            self.installTranslator(qt_translator)
        
        # Load app translations
        app_translator = QTranslator()
        translation_path = DATA_DIR / "translations" / f"mbulinux_{locale}.qm"
        if translation_path.exists():
            if app_translator.load(str(translation_path)):
                self.installTranslator(app_translator)
    
    def load_fonts(self):
        """Load custom fonts."""
        fonts_dir = DATA_DIR / "fonts"
        if fonts_dir.exists():
            for font_file in fonts_dir.glob("*.ttf"):
                QFontDatabase.addApplicationFont(str(font_file))
    
    def apply_style(self):
        """Apply application style based on settings."""
        theme = self.settings.get('theme', 'auto')
        
        if theme == 'auto':
            # Detect system theme
            pass  # Implement system theme detection
        
        # Load QSS file
        style_file = DATA_DIR / "styles" / f"{theme}.qss"
        if style_file.exists():
            with open(style_file, 'r') as f:
                self.setStyleSheet(f.read())
    
    def exec(self):
        """Execute application with cleanup."""
        exit_code = super().exec()
        self.save_settings()
        return exit_code