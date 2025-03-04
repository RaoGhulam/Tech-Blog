import sqlite3
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()


# # Read Contact Table ----------------------------------------------------------------------
# cursor.execute("SELECT * FROM Contact")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# # Read Post Table -------------------------------------------------------------------------
# cursor.execute("SELECT * FROM Pending_Post")
# rows = cursor.fetchall()

# for row in rows:
#     print(row)

# # Check ALl tables in the database-----------------------------------------------------------
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# for table in tables:
#     print(table[0])

# # Drop tables if they exist-----------------------------------------------------------------
# tables = ["pending__post", "post", "user", "contact", "posts"]

# for table in tables:
#     cursor.execute(f"DROP TABLE IF EXISTS {table};")

# # Delete a Table --------------------------------------------------------------------------
# cursor.execute("DROP TABLE IF EXISTS Post")
# conn.commit()

# # Delete a Table --------------------------------------------------------------------------
# cursor.execute("DROP TABLE IF EXISTS Pending_Post")
# conn.commit()

# # Delete a Table --------------------------------------------------------------------------
# cursor.execute("DROP TABLE IF EXISTS Contact")
# conn.commit()

# # Add rows in a Table ---------------------------------------------------------------------
# data = [
#     (1, "Introduction to Python", "A Beginner's Guide", "introduction-to-python", "Python is a versatile language.", "2025-02-28 12:00:00"),
#     (2, "Flask for Web Development", "Building Web Apps", "flask-web-development", "Flask is a lightweight web framework.", "2025-02-28 12:05:00"),
#     (3, "Machine Learning Basics", "Understanding ML Concepts", "machine-learning-basics", "ML enables computers to learn from data.", "2025-02-28 12:10:00"),
#     (4, "Deep Learning Explained", "Neural Networks Overview", "deep-learning-explained", "Deep learning powers AI advancements.", "2025-02-28 12:15:00"),
#     (5, "SQLAlchemy in Flask", "ORM for Databases", "sqlalchemy-in-flask", "SQLAlchemy simplifies database interactions.", "2025-02-28 12:20:00")
# ]
# cursor.executemany("INSERT INTO Post (sno, title, subtitle, slug, content, date) VALUES (?, ?, ?, ?, ?, ?)", data)
# conn.commit()

conn.close()