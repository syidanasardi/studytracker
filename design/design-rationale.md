# Identifier for Each Entity
decks: Surrogate Keys - gives stable identifier for each deck since name (which do not fit as identifier) might change along the way
cards: Surrogate Keys - gives stable identifier for each deck since currently other columns such as question and anser are not unique
tags: Surrogate Keys - gives stable identifier for each tags
card_tags: Composite Keys - used to identify pairs of card and tag, which uses their ids as card_tags' identifier
reviews: Surrogate key - gives stable identifier for each review to a card. Reviews are timestamped events. Multiple reviews can exist for the same card over time, so a composite key (card_id, user_id) wouldn't work. A surrogate key allows tracking review history.

# Many-to-Many relationship
This relationship can be found on cards and tags table. They are connected through card_tags table

# Two Decisions for Real Version
Add a users table which contains identifier, name, role (student or teacher)
Link students from users table to their assigned decks

# Data minimization
Do not collect personal data of the users such as their personal notes, IP Address, etc

# One more open question
Should a study_sessions table be created?
One idea if created - students will be connected to study_sessions and study_sessions will be connected to decks
If not created - students will directly be assigned to which decks they must complete

# Review Timestamp
Add created_at timestamp to capture when the review occurred
Study trackers need to track review frequency and spaced repetition. Without timestamps, you can't implement spaced repetition algorithms or track study patterns.

# Review Content
Rating (1-5) - Different from just tracking "was reviewed" — storing how well the student did helps with adaptive learning and identifying hard cards.