CREATE TABLE teachers (
  teacher_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  username VARCHAR NOT NULL UNIQUE,
  email VARCHAR NOT NULL UNIQUE,
  hash VARCHAR NOT NULL
);

CREATE TABLE students (
  student_id SERIAL PRIMARY KEY,
  student_name VARCHAR NOT NULL UNIQUE,
  questions_answered INTEGER [] DEFAULT '{}',
  submitted_answers VARCHAR [] DEFAULT '{}',
  results BOOLEAN [] DEFAULT '{}'
);

CREATE TABLE games (
  game_id SERIAL PRIMARY KEY,
  teacher INTEGER REFERENCES teachers ON DELETE CASCADE,
  students INTEGER [] DEFAULT '{}',
  game_name VARCHAR NOT NULL,
  question_list INTEGER []
);

CREATE TABLE questions (
  question_id SERIAL PRIMARY KEY,
  teacher INTEGER REFERENCES teachers ON DELETE CASCADE,
  question VARCHAR NOT NULL UNIQUE,
  choice_a VARCHAR NOT NULL,
  choice_b VARCHAR NOT NULL,
  choice_c VARCHAR NOT NULL,
  choice_d VARCHAR NOT NULL,
  answer VARCHAR NOT NULL
);
