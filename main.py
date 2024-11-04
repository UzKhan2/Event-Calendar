import sys
from PyQt6.QtWidgets import QApplication
from gui import ModernCalendar

def main():
    app = QApplication(sys.argv)
    window = ModernCalendar()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()