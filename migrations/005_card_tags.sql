CREATE TABLE card_tags (
  card_id INTEGER NOT NULL REFERENCES cards(id) ON DELETE CASCADE,
  tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (card_id, tag_id)
);

INSERT INTO card_tags (card_id, tag_id)
VALUES
  (1, 1),
  (2, 1)