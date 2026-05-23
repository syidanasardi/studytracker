from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import Form
from fastapi.responses import RedirectResponse

from .db import get_connection

import os
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import argon2
from fastapi import HTTPException
from .queries.users import create_user_query, fetch_user_by_email, fetch_user_by_id

from .queries.tags import create_tag_query, fetch_tag, fetch_all_tags, fetch_newest_tag, delete_tag_query, update_tag_query
from .queries.decks import fetch_all_decks, fetch_newest_deck, fetch_deck, create_deck_query, delete_deck_query, update_deck_query

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET", "dev-secret"))

def render(request: Request, template_name: str, **context):
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
    )

def get_current_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    with get_connection() as conn:
        return fetch_user_by_id(conn, user_id)
    
@app.get("/")
def index():
    return RedirectResponse("/login", status_code=303)

@app.get("/login")
def login_form(request: Request):
    return render(request, "login.html")

@app.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    with get_connection() as conn:
        user = fetch_user_by_email(conn, email)
        if not user or not argon2.verify(password, user["password_hash"]):
            return render(request, "login.html", error="Invalid credentials")
        request.session["user_id"] = user["id"]
    return RedirectResponse("/decks", status_code=303)

@app.get("/signup")
def signup_form(request: Request):
    return render(request, "signup.html")

@app.post("/signup")
def signup(request: Request, email: str = Form(...), password: str = Form(...)):
    password_hash = argon2.hash(password)
    with get_connection() as conn:
        existing = fetch_user_by_email(conn, email)
        if existing:
            return render(request, "signup.html", error="Email already registered")
        create_user_query(conn, email, password_hash)
        user = fetch_user_by_email(conn, email)
        request.session["user_id"] = user["id"]
    return RedirectResponse("/decks", status_code=303)

@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/decks", status_code=303)

# Deck endpoints
@app.get("/decks")
def list_decks(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    with get_connection() as conn:
        decks = fetch_all_decks(conn, user['id'])
    return render(request, "decks.html", decks=decks, current_user=user)


@app.get("/decks/newest")
def newest_deck(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    with get_connection() as conn:
        deck = fetch_newest_deck(conn, user['id'])

    return render(request, "newest_deck.html", deck=deck)

@app.post("/decks")
def create_deck(request: Request, name: str = Form(...), description: str = Form(...)):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    with get_connection() as conn:
        create_deck_query(conn, name, description, user['id'])

    return RedirectResponse("/decks", status_code=303)

@app.post("/decks/{deck_id}/delete")
def delete_deck(request: Request, deck_id: int):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    with get_connection() as conn:
        delete_deck_query(conn, deck_id)

    return RedirectResponse("/decks", status_code=303)

@app.get("/decks/{deck_id}/edit")
def show_edit_deck(request: Request, deck_id: int):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    with get_connection() as conn:
        deck = fetch_deck(conn, deck_id)

    return render(request, "deck_edit.html", deck=deck)

@app.post("/decks/{deck_id}/edit")
def update_deck(deck_id: int, name: str = Form(...), description: str = Form(...)):
    with get_connection() as conn:
        update_deck_query(conn, deck_id, name, description)

    return RedirectResponse("/decks", status_code=303)

# @app.get("/decks/{deck_id}")
# def show_deck(request: Request, deck_id: int):
#     with get_connection() as conn:
#         deck = conn.execute(t"""
#             SELECT id, name, description
#             FROM decks
#             WHERE id = {deck_id}
#             """).fetchone()

#         if deck is None:
#             return RedirectResponse("/decks", status_code=303)

#         cards = conn.execute(t"""
#             SELECT id, question, answer
#             FROM cards
#             WHERE deck_id = {deck_id}
#             ORDER BY id
#             """).fetchall()

#     return render(request, "deck_detail.html", deck=deck, cards=cards)

# Card endpoints
@app.post("/decks/{deck_id}/cards")
def create_card(
    deck_id: int,
    question: str = Form(...),
    answer: str = Form(...),
):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO cards (deck_id, question, answer)
            VALUES (%s, %s, %s)
            """, (deck_id, question, answer))

    return RedirectResponse(f"/decks/{deck_id}", status_code=303)

# card tags endpoints
@app.get("/cards/{card_id}")
def show_card(request: Request, card_id: int):
    with get_connection() as conn:
        card = conn.execute("""
            SELECT
              c.id,
              c.question,
              c.answer,
              d.id AS deck_id,
              d.name AS deck_name
            FROM cards AS c
            INNER JOIN decks AS d ON d.id = c.deck_id
            WHERE c.id = %s
            """, (card_id,)).fetchone()

        if card is None:
            return RedirectResponse("/decks", status_code=303)

        tags = conn.execute("""
            SELECT
              t.id,
              t.name
            FROM card_tags AS ct
            INNER JOIN tags AS t ON t.id = ct.tag_id
            WHERE ct.card_id = %s
            ORDER BY t.name
            """, (card_id,)).fetchall()

        available_tags = conn.execute("""
            SELECT
              t.id,
              t.name
            FROM tags AS t
            WHERE NOT EXISTS (
              SELECT 1
              FROM card_tags AS ct
              WHERE ct.card_id = %s             
                AND ct.tag_id = t.id
            )
            ORDER BY t.name
            """, (card_id,)).fetchall()

    return render(
        request,
        "card_detail.html",
        card=card,
        tags=tags,
        available_tags=available_tags,
    )

@app.post("/cards/{card_id}/tags")
def add_tag_to_card(card_id: int, tag_id: int = Form(...)):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO card_tags (card_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """, (card_id, tag_id))

    return RedirectResponse(f"/cards/{card_id}", status_code=303)

# Tags related endpoints
@app.get("/tags")
def list_tags(request: Request):
    with get_connection() as conn:
        tags = fetch_all_tags(conn)

    return render(request, "tags.html", tags=tags)

@app.get("/tags/newest")
def newest_tag(request: Request):
    with get_connection() as conn:
        tag = fetch_newest_tag(conn)

    return render(request, "newest_tag.html", tag=tag)

@app.post("/tags")
def create_tag(name: str = Form(...)):
    with get_connection() as conn:
        create_tag_query(conn, name)

    return RedirectResponse("/tags", status_code=303)

@app.post("/tags/{tag_id}/delete")
def delete_tag(tag_id: int):
    with get_connection() as conn:
        delete_tag_query(conn, tag_id)

    return RedirectResponse("/tags", status_code=303)

@app.get("/tags/{tag_id}/edit")
def show_edit_tag(request: Request, tag_id: int):
    with get_connection() as conn:
        tag = fetch_tag(conn, tag_id)

    return render(request, "tag_edit.html", tag=tag)

@app.post("/tags/{tag_id}/edit")
def update_tag(tag_id: int, name: str = Form(...)):
    with get_connection() as conn:
        update_tag_query(conn, tag_id, name)

    return RedirectResponse("/tags", status_code=303)


# Reviews endpoints
@app.post("/cards/{card_id}/reviews")
def create_review(card_id: int, rating: int = Form(...)):
    with get_connection() as conn:
        card = conn.execute(t"""
            SELECT deck_id FROM cards WHERE id = {card_id}
        """).fetchone()

        if card is None:
            return RedirectResponse(url="/decks", status_code=303)

        conn.execute(t"""
            INSERT INTO reviews (card_id, rating)
            VALUES ({card_id}, {rating})
        """)

    return RedirectResponse(url=f"/decks/{card['deck_id']}", status_code=303)

@app.get("/decks/{deck_id}")
def deck_detail(request: Request, deck_id: int):
    with get_connection() as conn:
        deck = conn.execute(t"""
            SELECT id, name FROM decks WHERE id = {deck_id}
        """).fetchone()

        cards = conn.execute(t"""
            SELECT
              c.id,
              c.question,
              c.answer,
              COUNT(r.id) AS review_count,
              ROUND(AVG(r.rating)::numeric, 1) AS average_rating
            FROM cards AS c
            LEFT JOIN reviews AS r ON r.card_id = c.id
            WHERE c.deck_id = {deck_id}
            GROUP BY c.id, c.question, c.answer
            ORDER BY c.id
        """).fetchall()

        other_decks = conn.execute(t"""
            SELECT id, name FROM decks WHERE id <> {deck_id} ORDER BY name
        """).fetchall()

    return render(request, "deck_detail.html", deck=deck, cards=cards, other_decks=other_decks)

# Dashboard endpoint
@app.get("/dashboard")
def dashboard(request: Request):
    with get_connection() as conn:
        deck_count = conn.execute(
            "SELECT COUNT(*) AS deck_count FROM decks"
        ).fetchone()['deck_count']

        card_count = conn.execute(
            "SELECT COUNT(*) AS card_count FROM cards"
        ).fetchone()['card_count']

        review_count = conn.execute(
            "SELECT COUNT(*) AS review_count FROM reviews"
        ).fetchone()['review_count']

        average_rating = conn.execute(
            "SELECT COALESCE(ROUND(AVG(rating), 2), 0) AS average_rating FROM reviews"
        ).fetchone()['average_rating']

        per_deck = conn.execute(
            """
            WITH card_counts AS (
              SELECT deck_id, COUNT(*) AS card_count
              FROM cards
              GROUP BY deck_id
            ),
            review_counts AS (
              SELECT c.deck_id, COUNT(*) AS review_count
              FROM cards AS c
              INNER JOIN reviews AS r ON r.card_id = c.id
              GROUP BY c.deck_id
            )
            SELECT
              d.id, d.name,
              COALESCE(cc.card_count, 0) AS card_count,
              COALESCE(rc.review_count, 0) AS review_count
            FROM decks AS d
            LEFT JOIN card_counts AS cc ON cc.deck_id = d.id
            LEFT JOIN review_counts AS rc ON rc.deck_id = d.id
            ORDER BY d.name
            """
        ).fetchall()

        recent_reviews = conn.execute(
            """
            SELECT
              d.name AS deck_name,
              c.question,
              r.rating
            FROM reviews AS r
            INNER JOIN cards AS c ON r.card_id = c.id
            INNER JOIN decks AS d ON c.deck_id = d.id
            ORDER BY r.reviewed_at DESC
            LIMIT 10
            """
        ).fetchall()

    return render(
        request,
        "dashboard.html",
        deck_count=deck_count,
        card_count=card_count,
        review_count=review_count,
        average_rating=average_rating,
        per_deck=per_deck,
        recent_reviews=recent_reviews,
    )

# Study session endpoints
@app.get("/decks/{deck_id}/study")
def study_question_view(request: Request, deck_id: int):
    with get_connection() as conn:
        deck = conn.execute(t"""
            SELECT id, name FROM decks WHERE id = {deck_id}
        """).fetchone()

        if deck is None:
            return RedirectResponse(url="/decks", status_code=303)

        next_card = conn.execute(t"""
            SELECT c.id, c.question
            FROM cards AS c
            LEFT JOIN reviews AS r ON r.card_id = c.id
            WHERE c.deck_id = {deck_id}
            GROUP BY c.id, c.question
            ORDER BY MAX(reviewed_at) ASC NULLS FIRST, c.id ASC
            LIMIT 1
        """).fetchone()

    if next_card is None:
        return render(request, "study_empty.html", deck=deck)

    return render(request, "study_question.html", deck=deck, card=next_card)

@app.get("/cards/{card_id}/study")
def study_answer_view(request: Request, card_id: int):
    with get_connection() as conn:
        card = conn.execute(t"""
            SELECT c.id, c.question, c.answer, c.deck_id, d.name AS deck_name
            FROM cards AS c
            INNER JOIN decks AS d ON d.id = c.deck_id
            WHERE c.id = {card_id}
        """).fetchone()

    if card is None:
        return RedirectResponse(url="/decks", status_code=303)

    return render(request, "study_answer.html", card=card)

@app.post("/cards/{card_id}/study/review")
def study_review(card_id: int, rating: int = Form(...)):
    with get_connection() as conn:
        with conn.transaction():
            card = conn.execute(t"""
                SELECT deck_id FROM cards WHERE id = {card_id}
            """).fetchone()

            if card is None:
                return RedirectResponse(url="/decks", status_code=303)

            conn.execute(t"""
                INSERT INTO reviews (card_id, rating)
                VALUES ({card_id}, {rating})
            """)

    return RedirectResponse(
        url=f"/decks/{card['deck_id']}/study", status_code=303
    )

# Moving cards to different decks
@app.post("/cards/{card_id}/move")
def move_card(card_id: int, target_deck_id: int = Form(...)):
    with get_connection() as conn:
        with conn.transaction():
            # Lock the target deck while we validate it exists.
            target_deck = conn.execute(t"""
                SELECT id FROM decks WHERE id = {target_deck_id} FOR UPDATE
            """).fetchone() 


            if target_deck is None:
                return RedirectResponse(
                    url=f"/cards/{card_id}", status_code=303
                )

            # Lock the source card so no concurrent move can change it.
            card = conn.execute(t"""
                SELECT id, deck_id FROM cards WHERE id = {card_id} FOR UPDATE
            """).fetchone()

            if card is None:
                return RedirectResponse(url="/decks", status_code=303)

            if card['deck_id'] == target_deck['id']:
                # No-op move; redirect back without writing.
                return RedirectResponse(
                    url=f"/decks/{card['deck_id']}", status_code=303
                )

            conn.execute(t"""
                UPDATE cards SET deck_id = {target_deck_id} WHERE id = {card_id}
            """)

    return RedirectResponse(url=f"/decks/{target_deck_id}", status_code=303)