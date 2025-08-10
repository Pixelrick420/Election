"""Database manager (SQLite) with simple connection handling and foreign key support."""
import sqlite3
import threading

DB_LOCK = threading.Lock()

class DatabaseManager:
    def __init__(self, db_path="election.db"):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_schema(self):
        with DB_LOCK:
            conn = self._connect()
            cur = conn.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Elections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    admin_password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    election_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    symbol_path TEXT,
                    is_nota INTEGER DEFAULT 0,
                    FOREIGN KEY (election_id) REFERENCES Elections (id) ON DELETE CASCADE
                )
            ''')

            try:
                cur.execute('ALTER TABLE Candidates ADD COLUMN is_nota INTEGER DEFAULT 0')
            except sqlite3.OperationalError:
                pass

            cur.execute('''
                CREATE TABLE IF NOT EXISTS Votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    election_id INTEGER NOT NULL,
                    candidate_id INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (election_id) REFERENCES Elections (id) ON DELETE CASCADE,
                    FOREIGN KEY (candidate_id) REFERENCES Candidates (id) ON DELETE CASCADE
                )
            ''')

            conn.commit()
            conn.close()

    def execute(self, query, params=None, fetch=False):
        with DB_LOCK:
            conn = self._connect()
            cur = conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)

            if fetch:
                rows = cur.fetchall()
                conn.close()
                return rows
            else:
                conn.commit()
                last = cur.lastrowid
                conn.close()
                return last