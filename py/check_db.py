import sqlite3

conn = sqlite3.connect('rentals.db')
c = conn.cursor()
c.execute("SELECT * FROM listings WHERE id = 1")
result = c.fetchone()
if result:
    print("Record with id=1 found:", result)
else:
    print("No record with id=1 found")
conn.close()