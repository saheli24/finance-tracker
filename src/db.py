import sqlite3
import os

#connects to finance data base
def connect():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "..", "db", "finance.db")
    return sqlite3.connect(db_path)

# call conn=connect() to open a connection to a database
#use a cursor such that python points at the database and excute the sql
def create_table():
    conn = connect()
    cursor = conn.cursor()
    
    #create a table called users else dont crash if it exists
    #auto increment ID and unique for each row
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    """)

    # each row = one purchase
    # (1, 1, 20.5, "Food", "2026-03-16", "Lunch")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        date TEXT,
        description TEXT
    )
    """)

    #save changes, sql changes are not saved automatically 
    # commit () = make it permanent
    conn.commit()

    #close the connection
    conn.close()

#only runs when python src/db.py
if __name__ == "__main__":
    create_table()
    print("Database + tables created!")

