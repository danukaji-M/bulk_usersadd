import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='userbot.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS added_members
                     (account_id INTEGER, date TEXT, count INTEGER, PRIMARY KEY (account_id, date))''')
        conn.commit()
        conn.close()

    def get_daily_count(self, account_id, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('SELECT count FROM added_members WHERE account_id = ? AND date = ?', (account_id, date))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def update_daily_count(self, account_id, count, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO added_members (account_id, date, count) VALUES (?, ?, ?)',
                  (account_id, date, count))
        conn.commit()
        conn.close()