import sqlite3
conn = sqlite3.connect('mydatabase.db')
cursor = conn.cursor()




# # Read Contact Table ----------------------------------------------------------------------
# cursor.execute("SELECT * FROM Contact")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)

# Read Post Table -------------------------------------------------------------------------
# cursor.execute("SELECT * FROM Pending_Post")
# rows = cursor.fetchall()

# for row in rows:
#     print(row)



# # Check ALl tables in the database-----------------------------------------------------------
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# for table in tables:
#     print(table[0])

# cursor.execute("PRAGMA table_info(Post);") 
# columns = cursor.fetchall()
# for column in columns:
#     print(column)

# Recreate the tables
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS Post (
#     sno INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     subtitle TEXT,
#     author TEXT NOT NULL,
#     slug TEXT NOT NULL UNIQUE,
#     content TEXT NOT NULL,
#     category TEXT NOT NULL DEFAULT 'General',
#     date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
# """)

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS Pending_Post (
#     sno INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     subtitle TEXT,
#     author TEXT NOT NULL,
#     slug TEXT NOT NULL UNIQUE,
#     content TEXT NOT NULL,
#     category TEXT NOT NULL DEFAULT 'General',
#     date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# );
# """)

# conn.commit()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# for table in tables:
#     print(table[0])

# Insert sample posts if the Post table is empty
# cursor.execute("SELECT COUNT(*) FROM Post;")
# post_count = cursor.fetchone()[0]

# if post_count == 0:
#   sample_data = [
#     (1, "Introduction to Python", "A Beginner's Guide", "intro-python", "Python is an amazing language!", "Programming", "2025-03-22 12:00:00", "Admin"),
#     (2, "Flask for Web Development", "Build Web Apps Easily", "flask-web", "Flask is a micro web framework.", "Web Development", "2025-03-22 12:05:00", "Admin"),
# ]

# cursor.executemany("INSERT INTO Post (sno, title, subtitle, slug, content, category, date, author) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_data)
# conn.commit()
# print("\nSample data inserted into Post table!")


# # Check if data is now available
# cursor.execute("SELECT * FROM Post;")
# posts = cursor.fetchall()
# print("\nPosts in database:")
# for post in posts:
#     print(post)





# cursor.execute("SELECT * FROM Post;")
# posts = cursor.fetchall()
# print("\nPosts in database:")
# for post in posts:
#     print(post)

# cursor.execute("SELECT * FROM Pending_Post;")
# pending_posts = cursor.fetchall()
# print("\nPending Posts in database:")
# for pending_post in pending_posts:
#     print(pending_post)


# # Drop tables if they exist-----------------------------------------------------------------
# tables = ["pending_post", "post", "user", "contact", "posts"]

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
#     (1, "Introduction to Python", "A Beginner's Guide", "introduction-to-python", "Python is a versatile language.","Programming", "2025-02-28 12:00:00"),
#     (2, "Flask for Web Development", "Building Web Apps", "flask-web-development", "Flask is a lightweight web framework.","Web Development", "2025-02-28 12:05:00"),
#     (3, "Machine Learning Basics", "Understanding ML Concepts", "machine-learning-basics", "ML enables computers to learn from data.","AI/ML", "2025-02-28 12:10:00"),
#     (4, "Deep Learning Explained", "Neural Networks Overview", "deep-learning-explained", "Deep learning powers AI advancements.","AI/ML", "2025-02-28 12:15:00"),
#     (5, "SQLAlchemy in Flask", "ORM for Databases", "sqlalchemy-in-flask", "SQLAlchemy simplifies database interactions.","Databases", "2025-02-28 12:20:00")
# ]
# cursor.executemany("INSERT INTO Post (sno, title, subtitle, slug, content, category, date) VALUES (?, ?, ?, ?, ?, ?,?)", data)
# conn.commit()

conn.close()