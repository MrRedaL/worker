import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', 'database.db')

def get_connection():
    # Helper to get db connection
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            health INTEGER DEFAULT 100,
            food INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT health, food FROM users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    
    if row is None:
        # Create user if they don't exist
        c.execute('INSERT INTO users (user_id, health, food) VALUES (?, ?, ?)', (user_id, 100, 0))
        conn.commit()
        health = 100
        food = 0
    else:
        health, food = row
        
    conn.close()
    return health, food

def update_user(user_id, health, food):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE users SET health = ?, food = ? WHERE user_id = ?', (health, food, user_id))
    conn.commit()
    conn.close()
