import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt

from main_window import SonicCalm

def main():
    # NOTE: In PySide6 (Qt 6), High DPI scaling is enabled by default.
    # The lines 'setAttribute(AA_EnableHighDpiScaling)' and 'AA_UseHighDpiPixmaps'
    # are deprecated and no longer needed.
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set up a sophisticated dark palette
    pal = QPalette()
    pal.setColor(QPalette.Window, QColor(12, 12, 20))
    pal.setColor(QPalette.WindowText, QColor(220, 220, 230))
    pal.setColor(QPalette.Base, QColor(18, 18, 28))
    pal.setColor(QPalette.AlternateBase, QColor(25, 25, 38))
    pal.setColor(QPalette.ToolTipBase, QColor(18, 18, 28))
    pal.setColor(QPalette.ToolTipText, QColor(220, 220, 230))
    pal.setColor(QPalette.Text, QColor(220, 220, 230))
    pal.setColor(QPalette.Button, QColor(24, 24, 40))
    pal.setColor(QPalette.ButtonText, QColor(220, 220, 230))
    pal.setColor(QPalette.BrightText, Qt.red)
    pal.setColor(QPalette.Highlight, QColor(0, 255, 200))
    pal.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(pal)

    win = SonicCalm()
    
    # Center window after show to ensure correct sizeHints
    win.show()
    r = app.primaryScreen().geometry()
    win.move((r.width() - win.width()) // 2, (r.height() - win.height()) // 2)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()