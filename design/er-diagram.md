# ER Diagram
erDiagram

    decks ||--o{ cards

    cards ||--o{ card_tags

    tags ||--o{ tags
    
    cards ||--o{ reviews

    decks {
        integer id
        string name
        string description
        timestamp created_at
    }

    cards {
        integer id
        integer deck_id
        string question
        string answer
        timestamp created_at
    }

    card_tags {
        integer card_id
        integer tag_id
    }

    tags {
        integer id
        string tag
        timestamp created_at
    }

    reviews {
        integer id
        integer card_id
        integer rating
        timestamp reviewed_at
    }

