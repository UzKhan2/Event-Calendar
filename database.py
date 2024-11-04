import sqlite3

class CalendarDatabase:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_database()
        
    def init_database(self):
        try:
            self.conn = sqlite3.connect('calendar_events.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    description TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            
    def close(self):
        if self.conn:
            self.conn.close()
            
    def add_event(self, date, time, description):
        self.cursor.execute('''
            INSERT INTO events (date, time, description)
            VALUES (?, ?, ?)
        ''', (date, time, description))
        self.conn.commit()
        
    def delete_event(self, date, time, description):
        self.cursor.execute('''
            DELETE FROM events 
            WHERE date = ? AND time = ? AND description = ?
        ''', (date, time, description))
        self.conn.commit()
        
    def get_events(self, date):
        self.cursor.execute('''
            SELECT time, description FROM events
            WHERE date = ?
            ORDER BY time
        ''', (date,))
        return self.cursor.fetchall()