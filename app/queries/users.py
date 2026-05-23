def create_user_query(conn, email, password_hash):
    conn.execute(
        t"""
        INSERT INTO users (email, password_hash)
        VALUES ({email}, {password_hash})
        """
    )

def fetch_user_by_email(conn, email):
    return conn.execute(
        t"SELECT id, email, password_hash FROM users WHERE email = {email}"
    ).fetchone()

def fetch_user_by_id(conn, user_id):
    return conn.execute(
        t"SELECT id, email, password_hash FROM users WHERE id = {user_id}"
    ).fetchone()