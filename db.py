"""
INTENTIONALLY VULNERABLE - FOR EDUCATIONAL/TESTING PURPOSES ONLY
This code demonstrates a SQL injection vulnerability.
DO NOT use in production.
"""

import sqlite3

def setup_db():
    """
    Create and initialize an in-memory SQLite database with a `users` table and two seeded user records for testing.
    
    Returns:
        sqlite3.Connection: Connection to the initialized in-memory database.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users VALUES (1, 'admin', 'secret123')")
    cursor.execute("INSERT INTO users VALUES (2, 'user', 'password')")
    conn.commit()
    return conn

def vulnerable_login(conn, username, password):
    """
    Perform a users table lookup using the provided credentials by embedding them directly into an SQL query string; this behavior is vulnerable to SQL injection.
    
    Parameters:
        conn (sqlite3.Connection): Database connection to use for the query.
        username (str): Username to match.
        password (str): Password to match.
    
    Returns:
        tuple or None: The first matching row from the users table as a tuple, or `None` if no match is found.
    """
    cursor = conn.cursor()
    # VULNERABLE: Direct string concatenation allows SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing: {query}")
    cursor.execute(query)
    return cursor.fetchone()

if __name__ == "__main__":
    conn = setup_db()
    