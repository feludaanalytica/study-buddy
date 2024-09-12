import sqlite3
from threading import Lock

class Database:
    _instance = None
    _lock = Lock()  # To make sure it's thread-safe

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-checked locking
                    cls._instance = super(Database, cls).__new__(cls)
                    cls._instance._initialize_db()
        return cls._instance

    def _initialize_db(self):
        """Initialize the database connection and create tables if they don't exist."""
        self.conn = sqlite3.connect('courses.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables if they do not already exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                course_name TEXT NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        ''')
        self.conn.commit()

    def get_cursor(self):
        """Get the cursor for executing queries."""
        return self.cursor

    def commit(self):
        """Commit the current transaction."""
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()
