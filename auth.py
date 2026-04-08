import sqlite3
import hashlib
from database import DB_NAME, init_db

# Ensure backend exists
init_db()

def hash_password(password):
    """Saltless SHA256 for rapid hackathon deployment."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, full_name, age):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password_hash, full_name, age) VALUES (?, ?, ?, ?)', 
                  (username, hash_password(password), full_name, age))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists. Please choose a different one."
    except Exception as e:
        conn.close()
        return False, f"Auth Error: {str(e)}"

def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id, full_name FROM users WHERE username = ? AND password_hash = ?', (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return True, user[0], user[1] or username
    return False, None, "Invalid username or password."
