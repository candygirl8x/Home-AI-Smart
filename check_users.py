import sqlite3

conn = sqlite3.connect("database/smart_home.db")   # Change the path if needed
cursor = conn.cursor()

cursor.execute("SELECT id, username, email FROM users")

users = cursor.fetchall()

print(users)

conn.close()