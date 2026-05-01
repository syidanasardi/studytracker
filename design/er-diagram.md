# ER Diagram
erDiagram
    decks ||--o{ cards
    cards ||--o{ card_tags
    tags ||--o{ tags

    decks {
        integer id
        string name
        string description
        date created_at
    }

    cards {
        integer id
        integer deck_id
        string question
        string answer
        date created_at
    }

    card_tags {
        integer card_id
        integer tag_id
    }

    tags {
        integer id
        string tag
        date created_at
    }

