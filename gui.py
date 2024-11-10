from datetime import datetime
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QComboBox
from database import CalendarDatabase
from PyQt6.QtCore import Qt, QSize, QByteArray, QDate
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QColor
from PyQt6.QtWidgets import (QMainWindow, QWidget, QCalendarWidget,
                            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QListWidget, QFrame, QToolButton, QApplication)

class TagColors:
    COLORS = {
        'Work': QColor('#f5a442'),       # Orange
        'Personal': QColor('#42f554'),   # Green
        'School': QColor('#ed1c24'),     # Red
        'Family': QColor('#4287f5'),     # Blue
        'Travel': QColor('#89CFF0'),     # White
        'NO TAG': QColor('#40404F')      # Dark Blue
    }
    
    @staticmethod
    def get_color(tag):
        return TagColors.COLORS.get(tag, QColor('#404040'))

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self, database):
        super().__init__()
        self.db = database
        self.event_dates = {}
        self.selected_dates = set()
        self.update_event_dates()
        self.clicked.connect(self.handle_date_clicked)
        
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.setGridVisible(True)
        
        header_format = self.headerTextFormat()
        header_font = header_format.font()
        header_font.setPixelSize(16)
        header_font.setBold(True)
        header_format.setFont(header_font)
        self.setHeaderTextFormat(header_format)
        
        self.setStyleSheet("""
            QCalendarWidget QTableView {
                outline: none;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1a1a1a;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #1a1a1a;
            }
            QCalendarWidget QTableView QHeaderView {
                background-color: #2f2f2f;
            }
            QCalendarWidget QTableView QHeaderView::section {
                color: white;
                padding: 6px;
                background-color: #2f2f2f;
                border: 1px solid #404040;
                font-size: 16px;
                padding: 10px 5px;
            }
        """)

    def get_complementary_color(self, color):
        hue = color.hue()
        complementary_hue = (hue + 180) % 360
        return QColor.fromHsv(complementary_hue, color.saturation(), color.value())
        
    def handle_date_clicked(self, date):
        date_str = date.toPyDate().isoformat()
        modifiers = QApplication.keyboardModifiers()
        
        if modifiers == Qt.KeyboardModifier.ControlModifier:
            if date_str in self.selected_dates:
                self.selected_dates.remove(date_str)
            else:
                self.selected_dates.add(date_str)
        else:
            self.selected_dates.clear()
            self.selected_dates.add(date_str)
            
        self.updateCells()
        
    def update_event_dates(self):
        try:
            first_day_of_grid = self.firstDayOfMonth(self.monthShown(), self.yearShown())
            while first_day_of_grid.dayOfWeek() > 1:
                first_day_of_grid = first_day_of_grid.addDays(-1)
            
            last_day_of_grid = first_day_of_grid.addDays(41)  # 6 weeks × 7 days - 1
            
            start_iso = first_day_of_grid.toPyDate().isoformat()
            end_iso = last_day_of_grid.toPyDate().isoformat()
            
            self.event_dates = {}
            current_date = first_day_of_grid
            
            # Iterate through all visible dates
            while current_date <= last_day_of_grid:
                current_iso = current_date.toPyDate().isoformat()
                events = self.db.get_events(current_iso)
                
                if events:
                    tag = None
                    for event in events:
                        if event[2]:  # Check if event has a tag
                            tag = event[2]
                            break
                    
                    self.event_dates[current_iso] = {
                        'count': len(events),
                        'tag': tag if tag else 'NO TAG'
                    }
                
                current_date = current_date.addDays(1)
            
        except Exception as e:
            print(f"Error in update_event_dates: {e}")
            self.event_dates = {}
    
    def firstDayOfMonth(self, month, year):
        return QDate(year, month, 1)
    
    def paintCell(self, painter, rect, date):
        date_str = date.toPyDate().isoformat()
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        background_color = QColor('#2f2f2f')  # Default background
        
        if date_str in self.selected_dates:
            background_color = QColor('#666666')
            painter.fillRect(rect, background_color)
            painter.setPen(Qt.GlobalColor.white)
        elif date_str in self.event_dates:
            tag = self.event_dates[date_str]['tag']
            background_color = TagColors.get_color(tag)
            painter.fillRect(rect, background_color)
            painter.setPen(Qt.GlobalColor.white)
        else:
            painter.fillRect(rect, background_color)
            if date.dayOfWeek() in [6, 7]:  # Saturday and Sunday
                painter.setPen(QColor('#ed1c24'))  # Red for weekends
            else:
                painter.setPen(Qt.GlobalColor.white)
        
        font = painter.font()
        font.setPixelSize(int(rect.height() * 0.3))
        painter.setFont(font)
        
        number_text = str(date.day())
        painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignAbsolute, number_text)
        
        text_rect = painter.boundingRect(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, number_text)
        
        if date_str in self.event_dates:
            event_count = self.event_dates[date_str]['count']
            dot_size = min(rect.width(), rect.height()) // 20
            
            dot_color = self.get_complementary_color(background_color)
            painter.setBrush(dot_color)
            painter.setPen(dot_color)
            
            # Calculate dots layout
            dots_per_row = 5
            num_rows = (event_count + dots_per_row - 1) // dots_per_row
            num_rows = min(num_rows, 2)  # Maximum 2 rows
            
            start_y = text_rect.bottom() + dot_size
            
            for row in range(num_rows):
                dots_in_this_row = min(dots_per_row, event_count - (row * dots_per_row))
                total_width = dots_in_this_row * (dot_size * 2)
                start_x = rect.center().x() - (total_width // 2)
                
                for col in range(dots_in_this_row):
                    x = start_x + (col * dot_size * 2)
                    y = start_y + (row * dot_size * 2)
                    painter.drawEllipse(x, y, dot_size, dot_size)
        
        painter.restore()
        
    def clear_selection(self):
        self.selected_dates.clear()
        self.updateCells()

    def on_selection_changed(self):
        self.update_event_dates()
        self.updateCells()  
              
class ModernCalendar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = CalendarDatabase()
        self.init_ui()
        
    def _create_svg_arrows(self):
        # Left arrow icon
        left_arrow_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" fill="white"/>
        </svg>
        """
        
        # Right arrow icon
        right_arrow_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z" fill="white"/>
        </svg>
        """
        
        size = QSize(24, 24)
        
        # Create left icon
        left_pixmap = QPixmap(size)
        left_pixmap.fill(Qt.GlobalColor.transparent)
        left_renderer = QSvgRenderer(QByteArray(left_arrow_svg.encode()))
        painter = QPainter(left_pixmap)
        left_renderer.render(painter)
        painter.end()
        left_icon = QIcon(left_pixmap)
        
        # Create right icon
        right_pixmap = QPixmap(size)
        right_pixmap.fill(Qt.GlobalColor.transparent)
        right_renderer = QSvgRenderer(QByteArray(right_arrow_svg.encode()))
        painter = QPainter(right_pixmap)
        right_renderer.render(painter)
        painter.end()
        right_icon = QIcon(right_pixmap)
        
        return left_icon, right_icon
        
    def init_ui(self):
        self.setWindowTitle("Calendar")
        self.setMinimumSize(1200, 800)
        
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left card (calendar section)
        calendar_card = QFrame()
        calendar_card.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        self._setup_calendar_section(calendar_card)
        main_layout.addWidget(calendar_card, 7)
        
        # Right card (events section)
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
        
        self.calendar = CustomCalendarWidget(self.db)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.clicked.connect(self.update_events)
        self.calendar.currentPageChanged.connect(self.on_month_changed)
        self.calendar.setMinimumWidth(parent.width() - 40)
        
        nav_bar = self.calendar.findChild(QWidget, "qt_calendar_navigationbar")
        if nav_bar:
            prev_button = nav_bar.findChild(QToolButton, "qt_calendar_prevmonth")
            next_button = nav_bar.findChild(QToolButton, "qt_calendar_nextmonth")
            
            if prev_button and next_button:
                left_icon, right_icon = self._create_svg_arrows()
                prev_button.setIcon(left_icon)
                prev_button.setIconSize(QSize(24, 24))
                next_button.setIcon(right_icon)
                next_button.setIconSize(QSize(24, 24))
        
        calendar_layout.addWidget(self.calendar)
        layout.addWidget(calendar_container)
        
    def _setup_events_section(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(2)
        
        events_label = QLabel("Events Details")
        events_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
            }
        """)
        events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(events_label)
        
        self.events_list = QListWidget()
        self.events_list.setMinimumHeight(150)
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
                text-align: center;
            }
            QListWidget::item:selected {
                background-color: #ed1c24;
                color: white;
            }
        """)
        layout.addWidget(self.events_list)

        spacer = QWidget()
        spacer.setFixedHeight(100)  # Add dummy space
        layout.addWidget(spacer)
            
        
        # Event Title
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title_label = QLabel("Event Title:")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 0;
                margin: 0;
            }
        """)
        title_layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter event title")
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                margin: 0;
            }
            QLineEdit:focus {
                border: 1px solid #ed1c24;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        title_layout.addWidget(self.title_input)
        layout.addWidget(title_container)
        
        # Time Input
        time_container = QWidget()
        time_layout = QVBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(2)
        
        time_label = QLabel("Time (HH:MM):")
        time_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 0;
                margin: 0;
            }
        """)
        time_layout.addWidget(time_label)
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Optional (e.g., 14:30)")
        self.time_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                margin: 0;
            }
            QLineEdit:focus {
                border: 1px solid #ed1c24;
            }
            QLineEdit::placeholder {
                color: #808080;
            }
        """)
        time_layout.addWidget(self.time_input)
        layout.addWidget(time_container)
        
        # Tag Selection
        tag_container = QWidget()
        tag_layout = QVBoxLayout(tag_container)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(2)
        
        tag_label = QLabel("Tag:")
        tag_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 0;
                margin: 0;
            }
        """)
        tag_layout.addWidget(tag_label)
        
        self.tag_combo = QComboBox()
        self.tag_combo.addItems(['No Tag', 'Work', 'Personal', 'School', 'Family', 'Travel'])
        self.tag_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 4px;
                color: white;
                font-size: 14px;
                margin: 0;
            }
            QComboBox:drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #252525;
                color: white;
                selection-background-color: #ed1c24;
            }
        """)
        tag_layout.addWidget(self.tag_combo)
        layout.addWidget(tag_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.add_button = QPushButton("Add Event")
        self.add_button.clicked.connect(self.add_event)
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #ed1c24;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #ff2c35;
            }
            QPushButton:pressed {
                background-color: #d31820;
            }
        """)
        
        self.delete_button = QPushButton("Delete Event")
        self.delete_button.clicked.connect(self.delete_event)
        self.delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                margin-right: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #363636;
            }
        """)
        
        self.clear_selection_button = QPushButton("Clear Selection")
        self.clear_selection_button.clicked.connect(self.clear_selection)
        self.clear_selection_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_selection_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #363636;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
        """)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_selection_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _apply_styles(self):
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: #1a1a1a;
                border: none;
            }
            
            QCalendarWidget QWidget {
                alternate-background-color: #1a1a1a;
                color: white;
            }
            
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #1a1a1a;
                min-height: 50px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QCalendarWidget QToolButton {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: transparent;
                padding: 10px;
            }
            
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: white;
                background-color: #1a1a1a;
                border: 1px solid #404040;
            }
            
            QCalendarWidget QSpinBox {
                color: white;
                background-color: #1a1a1a;
                selection-background-color: #ed1c24;
                selection-color: white;
            }
            
            QCalendarWidget QTableView {
                background-color: #2f2f2f;
                selection-background-color: #ed1c24;
                selection-color: white;
                border: none;
                outline: none;
            }
            
            QCalendarWidget QTableView QHeaderView::section {
                color: white;
                padding: 6px;
                background-color: #2f2f2f;
                border: 1px solid #404040;
            }
            
            QCalendarWidget QTableView::item {
                border: 1px solid #404040;
                padding: 5px;
            }
            
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                selection-background-color: #ed1c24;
                selection-color: white;
            }
            
            QCalendarWidget QAbstractItemView:disabled {
                color: #666;
            }
            
            QCalendarWidget QToolButton::menu-indicator { 
                image: none;
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

    def on_month_changed(self):
        self.calendar.update_event_dates()
        self.calendar.updateCells()

    def validate_time_format(self, time_str):
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False
            
    def delete_event(self):
        try:
            current_item = self.events_list.currentItem()
            if not current_item:
                return
                
            text = current_item.text()
            
            if ' - ' in text:
                if '[' in text:
                    # Has time and tag
                    main_part = text.split(' [')[0]
                    time = main_part.split(' - ')[0]
                    description = main_part.split(' - ')[1]
                else:
                    # Has time, no tag
                    time = text.split(' - ')[0]
                    description = text.split(' - ')[1]
            else:
                if '[' in text:
                    # No time, has tag
                    description = text.split(' [')[0]
                    time = None
                else:
                    # Only description
                    description = text
                    time = None
            
            date = self.calendar.selectedDate().toPyDate().isoformat()
            self.db.delete_event(date, description, time)
            
            self.calendar.update_event_dates()
            self.calendar.updateCells()
            self.update_events()
            
        except Exception as e:
            print(f"Error: {str(e)}")

    def add_event(self):
        try:
            time = self.time_input.text().strip()
            description = self.title_input.text().strip()
            tag = self.tag_combo.currentText() if self.tag_combo.currentText() != 'No Tag' else None
            
            if not description:
                return

            # Validate time if inputted
            if time and not self.validate_time_format(time):
                return

            # If time is empty string, set to None
            time = time if time else None
            
            # Add event to all selected dates
            selected_dates = self.calendar.selected_dates
            if not selected_dates:  # If no dates selected, use current date
                selected_dates = {self.calendar.selectedDate().toPyDate().isoformat()}
            
            for date in selected_dates:
                self.db.add_event(date, description, time, tag)
            
            self.title_input.clear()
            self.time_input.clear()
            self.calendar.clear_selection()
            
            self.calendar.update_event_dates()
            self.calendar.updateCells()
            self.update_events()
            
        except Exception as e:
            print(f"Error: {str(e)}")

    def clear_selection(self):
        self.calendar.clear_selection()

    def update_events(self):
        try:
            self.events_list.clear()
            date = self.calendar.selectedDate().toPyDate().isoformat()
            
            events = self.db.get_events(date)
            for event in events:
                time, description, tag = event
                if time and tag:
                    item_text = f"{time} - {description} [{tag}]"
                elif time:
                    item_text = f"{time} - {description}"
                elif tag:
                    item_text = f"{description} [{tag}]"
                else:
                    item_text = description
                self.events_list.addItem(item_text)
                
        except Exception as e:
            print(f"Error: {str(e)}")
            
    def closeEvent(self, event):
        self.db.close()
        event.accept()