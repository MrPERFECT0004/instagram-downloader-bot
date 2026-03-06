import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER UNIQUE
)
""")

conn.commit()


def add_user(user_id):

    try:
        cursor.execute("INSERT INTO users(user_id) VALUES(?)",(user_id,))
        conn.commit()
    except:
        pass


def get_users():

    cursor.execute("SELECT user_id FROM users")
    return cursor.fetchall()


def get_users_count():

    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]










