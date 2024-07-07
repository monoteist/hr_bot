import sqlite3

conn = sqlite3.connect('db.sqlite3')

cursor = conn.cursor()

cursor.execute('delete from users;')
conn.commit()
cursor.close()
conn.close()