CREATE TABLE games (
  game_id SERIAL PRIMARY KEY,
  teacher VARCHAR NOT NULL,
  game_name VARCHAR NOT NULL,
  question_list INTEGER []
);

CREATE TABLE questions (
  question_id SERIAL PRIMARY KEY,
  question VARCHAR NOT NULL UNIQUE,
  choice_a VARCHAR NOT NULL,
  choice_b VARCHAR NOT NULL,
  choice_c VARCHAR NOT NULL,
  choice_d VARCHAR NOT NULL,
  answer VARCHAR NOT NULL
);

CREATE TABLE answers (
  answer_id SERIAL PRIMARY KEY,
  answer INTEGER REFERENCES questions,
  game_played INTEGER REFERENCES games ON DELETE CASCADE,
  student VARCHAR NOT NULL DEFAULT 'Rachel',
  submitted_answer VARCHAR NOT NULL,
  correct BOOLEAN
);

CREATE TABLE users (
  user_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  username VARCHAR NOT NULL UNIQUE,
  email VARCHAR NOT NULL UNIQUE,
  hash VARCHAR NOT NULL
);
