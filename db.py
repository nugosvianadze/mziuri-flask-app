import sqlite3

def init_db():
    conn = sqlite3.connect("instances/mziuri.db")
    with open("schema.sql") as f:
        conn.executescript(f.read())
    conn.close()
