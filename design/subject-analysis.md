# Candidate Entities
decks, tags, cards, card_tags, reviews

# Candidate Relationship
One deck can have many cards
One card may be referred in card_tags zero or more times
cards and tags have many-to-many relationship
each card can have multiple reviews

# Candidate Events
User may create new decks
User may edit existing decks
User may delete existing decks
User may create new tags
User may edit existing tags
User may delete existing tags

# Business Rules
Each card must have a question and an answer
Newest decks will return the newest deck created based on the time in which the decks are created
The scale of rating in review is 1 to 5 inclusive

# Open Questions
Can a card have no tags?
Can a deck be created without a description?
Should the system remember deleted decks?
Ho many reviews can a user make to one card?

# Likely Application Queries
Cards in a given deck
Tags in a given
Question of the most recent card created in a certain deck
What are the reviews of a certain card in a particular decks