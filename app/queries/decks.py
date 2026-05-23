def fetch_all_decks(conn, user_id):
    return conn.execute(
        t"SELECT id, name, description FROM decks WHERE user_id = {user_id} ORDER BY name"
    ).fetchall()


def fetch_newest_deck(conn, user_id):
    return conn.execute(
        t"SELECT id, name, description FROM decks WHERE user_id = {user_id} ORDER BY created_at DESC, id DESC LIMIT 1"
    ).fetchone()


def fetch_deck(conn, deck_id):
    return conn.execute(
        "SELECT id, name, description FROM decks WHERE id = %s",
        (deck_id,)
    ).fetchone()


def create_deck_query(conn, name, description, user_id):
    return conn.execute(
        t"INSERT INTO decks (name, description, user_id) VALUES ({name}, {description}, {user_id})"
    )


def delete_deck_query(conn, deck_id):
    return conn.execute(
        "DELETE FROM decks WHERE id = %s",
        (deck_id,)
    )


def update_deck_query(conn, deck_id, name, description):
    return conn.execute(
        "UPDATE decks SET name = %s, description = %s WHERE id = %s",
        (name, description, deck_id)
    )