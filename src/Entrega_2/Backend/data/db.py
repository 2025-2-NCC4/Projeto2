import os, sqlite3

def get_db_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "pomodoroplus.db")

def get_connection():
    connection = sqlite3.connect(get_db_path())
    connection.row_factory=sqlite3.Row
    return connection