# db.py
import sqlite3
from flask import g

DB_PATH = "data/picmoney.db"

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        # 🔧 Se o driver devolver bytes, decodifica como UTF-8 (troca inválidos por � em último caso)
        conn.text_factory = lambda b: b.decode("utf-8", "replace") if isinstance(b, (bytes, bytearray)) else b
        g.db = conn
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
