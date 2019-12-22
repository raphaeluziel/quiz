import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# This looks for secret stuff in a .env file
from dotenv import load_dotenv
load_dotenv()

# Check for environment variable
if not os.getenv("QUIZDB_URL"):
    raise RuntimeError("QUIZDB_URL is not set")

# Setup database connection
engine = create_engine(os.getenv("QUIZDB_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    #f = open("questions.csv")
    #reader = csv.reader(f)

    question_parts = []
    question = []

    with open('questions.csv') as f:
        reader = csv.reader(f)
        for x in reader:
            try:
                x[0]
            except:
                question.append(question_parts)
                question_parts = []
            else:
                question_parts.append(x[0])

    for q in question:
        db.execute("INSERT INTO questions (teacher, question, choice_a, choice_b, choice_c, choice_d, answer) \
                   VALUES (:teacher, :question, :choice_a, :choice_b, :choice_c, :choice_d, :answer)",
                   {"teacher": 3, "question":q[0], "choice_a":q[1], "choice_b":q[2], "choice_c":q[3], "choice_d":q[4], "answer":q[5]})

        print('Added {} to database'.format({ q[0] })) # for older python versions
        db.commit()

if __name__ == "__main__":
    main()
