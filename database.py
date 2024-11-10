import sqlite3

class CalendarDatabase:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_database()
        
    def init_database(self):
        try:
            self.conn = sqlite3.connect('calendar.db')
            self.cursor = self.conn.cursor()

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT,
                    description TEXT NOT NULL,
                    tag TEXT
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            
    def close(self):
        if self.conn:
            self.conn.close()
            
    def add_event(self, date, description, time=None, tag=None):
        self.cursor.execute('''
            INSERT INTO events (date, time, description, tag)
            VALUES (?, ?, ?, ?)
        ''', (date, time, description, tag))
        self.conn.commit()
        
    def delete_event(self, date, description, time=None):
        if time:
            self.cursor.execute('''
                DELETE FROM events 
                WHERE date = ? AND time = ? AND description = ?
            ''', (date, time, description))
        else:
            self.cursor.execute('''
                DELETE FROM events 
                WHERE date = ? AND description = ? AND time IS NULL
            ''', (date, description))
        self.conn.commit()
        
    def get_events(self, date):
        self.cursor.execute('''
            SELECT time, description, tag FROM events
            WHERE date = ?
            ORDER BY COALESCE(time, '99:99')
        ''', (date,))
        return self.cursor.fetchall()
    
    def get_events_by_month_with_tags(self, start_date, end_date):
        self.cursor.execute('''
            SELECT DISTINCT date, COALESCE(tag, 'personal') as tag FROM events 
            WHERE date >= ? AND date <= ?
        ''', (start_date, end_date))
        return self.cursor.fetchall()
    