CREATE TABLE teachers (
  teacher_id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  username VARCHAR NOT NULL UNIQUE,
  email VARCHAR NOT NULL UNIQUE,
  hash VARCHAR NOT NULL,
  active_game VARCHAR DEFAULT 'No Game Being Played'
);

CREATE TABLE students (
  student_id SERIAL PRIMARY KEY,
  student_name VARCHAR NOT NULL,
  students_teacher INTEGER REFERENCES teachers ON DELETE CASCADE,
  students_active_game VARCHAR DEFAULT 'No Game Being Played',
  questions_answered INTEGER [] DEFAULT '{}',
  submitted_answers VARCHAR [] DEFAULT '{}',
  results BOOLEAN [] DEFAULT '{}',
  UNIQUE (student_name, students_teacher)
);

CREATE TABLE games (
  game_id SERIAL PRIMARY KEY,
  teacher INTEGER REFERENCES teachers ON DELETE CASCADE,
  students INTEGER [] DEFAULT '{}',
  game_name VARCHAR NOT NULL,
  question_list INTEGER [],
  UNIQUE (game_name, teacher)
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
