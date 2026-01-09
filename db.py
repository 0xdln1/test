"""
INTENTIONALLY VULNERABLE - FOR EDUCATIONAL/TESTING PURPOSES ONLY
This code demonstrates a SQL injection vulnerability.
DO NOT use in production.
"""

import sqlite3

def setup_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret123')")
    cursor.execute("INSERT INTO users VALUES (2, 'user', 'password')")
    conn.commit()
    return conn

def vulnerable_login(conn, username, password):
    cursor = conn.cursor()
    # VULNERABLE: Direct string concatenation allows SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing: {query}")
    cursor.execute(query)
    return cursor.fetchone()

if __name__ == "__main__":
    conn = setup_db()
    