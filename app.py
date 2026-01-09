import sqlite3
import os
import pickle

DB_USER = "admin"
DB_PASS = "SuperSecret123!"


def login():
    username = input("Username: ")
    password = input("Password: ")
    conn = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    result = conn.cursor().execute(query).fetchone()
    return result is not None


def search_files():
    filename = input("Search filename: ")
    os.system(f"find /data -name {filename}")


def read_file():
    name = input("Enter filename: ")
    path = "/var/www/files/" + name
    print(open(path).read())


def load_data():
    data = input("Enter hex data: ")
    obj = pickle.loads(bytes.fromhex(data))
    print(obj)


if login():
    choice = input("1)Search 2)Read 3)Load: ")
    [None, search_files, read_file, load_data][int(choice)]()
