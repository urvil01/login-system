import sqlite3

conn = sqlite3.connect("database.db")

cur = conn.cursor()

cur.execute("DELETE FROM users")

cur.execute("DELETE FROM sqlite_sequence WHERE name='users'")

conn.commit()

print("Database Reset Complete")

conn.close()