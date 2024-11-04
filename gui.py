from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QCalendarWidget,
                            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QListWidget, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import CalendarDatabase

class ModernCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = CalendarDatabase()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Calendar")
        self.setMinimumSize(1200, 800)
        
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        calendar_card = QFrame()
        calendar_card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        self._setup_calendar_section(calendar_card)
        main_layout.addWidget(calendar_card, 7)
        
        events_card = QFrame()
        events_card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self._setup_events_section(events_card)
        main_layout.addWidget(events_card, 3)
        
        self._apply_styles()
        self.update_events()
        self.showMaximized()

    def _setup_calendar_section(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header = QLabel("Calendar")
        header.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 15px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(header)
        
        calendar_container = QWidget()
        calendar_layout = QVBoxLayout(calendar_container)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.calendar = QCalendarWidget()
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.clicked.connect(self.update_events)
        self.calendar.setMinimumWidth(parent.width() - 40)
        
        calendar_layout.addWidget(self.calendar)
        layout.addWidget(calendar_container)
        
    def _setup_events_section(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        
        events_label = QLabel("Events")
        events_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 15px;
            }
        """)
        layout.addWidget(events_label)
        
        self.events_list = QListWidget()
        layout.addWidget(self.events_list)
        
        # Add Event Section
        add_event_label = QLabel("Add New Event")
        add_event_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding-top: 15px;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(add_event_label)
        
        title_label = QLabel("Event Title:")
        title_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter event title")
        layout.addWidget(self.title_input)
        
        time_label = QLabel("Time (HH:MM):")
        time_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(time_label)
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g., 14:30")
        layout.addWidget(self.time_input)
        
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Event")
        self.add_button.clicked.connect(self.add_event)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.delete_button = QPushButton("Delete Event")
        self.delete_button.clicked.connect(self.delete_event)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def _apply_styles(self):
        self.calendar.setStyleSheet("""
            /* Main Calendar Widget */
            QCalendarWidget {
                background-color: #1a1a1a;
                border: none;
            }
            
            /* Calendar table and header container */
            QCalendarWidget QWidget {
                alternate-background-color: #1a1a1a;
                color: white;
            }
            
            /* Navigation bar (month/year section) */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1a1a1a;
                min-height: 50px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            /* Month/Year buttons */
            QCalendarWidget QToolButton {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
                padding: 10px;
            }
            
            /* Previous month button */
            QCalendarWidget QToolButton::left-arrow {
                background-color: transparent;
                width: 24px;
                height: 24px;
                border: none;
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z' fill='white'/%3E%3C/svg%3E");
            }
            
            /* Next month button */
            QCalendarWidget QToolButton::right-arrow {
                background-color: transparent;
                width: 24px;
                height: 24px;
                border: none;
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z' fill='white'/%3E%3C/svg%3E");
            }
            
            /* Hover states for arrows */
            QCalendarWidget QToolButton::left-arrow:hover,
            QCalendarWidget QToolButton::right-arrow:hover {
                background-color: rgba(237, 28, 36, 0.1);
                border-radius: 12px;
            }
            
            QCalendarWidget QToolButton::menu-indicator { 
                image: none;
            }
            
            /* Calendar grid */
            QCalendarWidget QTableView {
                background-color: #2f2f2f;
                selection-background-color: #ed1c24;
                selection-color: white;
                border: none;
                outline: none;
            }
            
            /* Headers (Mon, Tue, etc) */
            QCalendarWidget QTableView QHeaderView::section {
                color: white;
                padding: 6px;
                background-color: #2f2f2f;
                border: 1px solid #404040;
            }
            
            /* Grid cells */
            QCalendarWidget QTableView::item {
                border: 1px solid #404040;
            }
            
            /* Days from current month */
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                selection-background-color: #ed1c24;
                selection-color: white;
            }
            
            /* Days from other months */
            QCalendarWidget QAbstractItemView:disabled {
                color: #666;
            }
            
            /* Selected date */
            QCalendarWidget QTableView::item:selected {
                background-color: #ed1c24;
                color: white;
            }
            
            QCalendarWidget QMenu {
                background-color: #2f2f2f;
                color: white;
            }
        """)
        
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: #ed1c24;
                color: white;
            }
        """)
        
        input_style = """
            QLineEdit {
                padding: 8px;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                margin: 5px 0;
            }
            QLineEdit:focus {
                border: 1px solid #ed1c24;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """
        self.title_input.setStyleSheet(input_style)
        self.time_input.setStyleSheet(input_style)
        
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #ed1c24;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #ff2c35;
            }
            QPushButton:pressed {
                background-color: #d31820;
            }
        """)
        
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #363636;
            }
        """)

    def validate_time_format(self, time_str):
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
            
    def add_event(self):
        try:
            date = self.calendar.selectedDate().toPyDate()
            time = self.time_input.text().strip()
            description = self.title_input.text().strip()
            
            if not description or not time or not self.validate_time_format(time):
                return

            self.db.add_event(date.isoformat(), time, description)
            self.title_input.clear()
            self.time_input.clear()
            self.update_events()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def delete_event(self):
        try:
            current_item = self.events_list.currentItem()
            if not current_item:
                return
                
            text = current_item.text()
            time = text.split(' - ')[0]
            description = text.split(' - ')[1]
            date = self.calendar.selectedDate().toPyDate().isoformat()
            
            self.db.delete_event(date, time, description)
            self.update_events()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def update_events(self):
        try:
            self.events_list.clear()
            date = self.calendar.selectedDate().toPyDate().isoformat()
            
            events = self.db.get_events(date)
            for event in events:
                self.events_list.addItem(f"{event[0]} - {event[1]}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def closeEvent(self, event):
        self.db.close()
        event.accept()