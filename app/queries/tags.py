def fetch_all_tags(conn):
    return conn.execute(
        "SELECT id, name FROM tags ORDER BY name"
    ).fetchall()

def fetch_newest_tag(conn):
    return conn.execute(
        "SELECT id, name FROM tags ORDER BY created_at DESC, id DESC LIMIT 1"
    ).fetchone()

def create_tag_query(conn, name):
    return conn.execute(t"""
                    INSERT INTO tags (name)
                    VALUES ({name})
                    """)

def delete_tag_query(conn, tag_id):
    return conn.execute(t"DELETE FROM tags WHERE id = {tag_id}")

def fetch_tag(conn, tag_id):
    return conn.execute(
            t"SELECT id, name FROM tags WHERE id = {tag_id}"
        ).fetchone()

def update_tag_query(conn, tag_id, name):
    return conn.execute(t"""
        UPDATE tags
        SET name = {name}
        WHERE id = {tag_id}
    """)