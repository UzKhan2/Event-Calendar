import sys
from gui import ModernCalendar
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = ModernCalendar()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()