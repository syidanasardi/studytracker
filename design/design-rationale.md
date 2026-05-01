# Identifier for Each Entity
decks: Surrogate Keys - gives stable identifier for each deck since name (which do not fit as identifier) might change along the way
cards: Surrogate Keys - gives stable identifier for each deck since currently other columns such as question and anser are not unique
tags: Surrogate Keys - gives stable identifier for each tags
card_tags: Composite Keys - used to identify pairs of card and tag, which uses their ids as card_tags' identifier

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