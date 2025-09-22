from backend.database import get_connection

def create_user(username, password):
    if not username or not password:
        return None
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        return cur.lastrowid
    except Exception:
        return None
    finally:
        conn.close()

def validate_login(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
