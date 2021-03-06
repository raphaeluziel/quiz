import os
import json
import requests
import datetime
import sys

# To enable websockets in VPS
import eventlet
from eventlet import wsgi

from flask import Flask, Response, render_template, request, redirect, session, url_for, jsonify, flash
from flask_session import Session
from datetime import timedelta
from flask_socketio import SocketIO, emit, rooms, join_room, leave_room
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Check for environment variable
if not os.getenv("QUIZDB_URL"):
    raise RuntimeError("QUIZDB_URL is not set")

# Setup connections for sockets and main app
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=3)
app.config["SESSION_FILE_THRESHOLD"] = 500
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

# Setup database connection
engine = create_engine(os.getenv("QUIZDB_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    """Render home page"""

    return render_template("index.html")

@app.route("/error")
def error():

    """Bug in my code should end up taking user here instead of a crash"""

    return render_template("error.html")



""" ***********************TEACHER LOGIN SECTION ************************** """

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("teacher_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():

    """Log user in"""

    # Forget any user # ID:
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure user sent username and password
        if not request.form.get("username"):
            message = "you must enter a username"
            return render_template("login.html", message=message)
        if not request.form.get("password"):
            message = "please enter your password"
            return render_template("login.html", message=message)

        # Query database for user
        teacher = db.execute("SELECT * FROM teachers WHERE username = :username",
            {"username":request.form.get("username")}).fetchone()

        # Is username in database?
        if not teacher:
            message = "username does not exist"
            return  render_template("login.html", message=message)

        # Does password match username?
        if not check_password_hash(teacher.hash, request.form.get("password")):
            message = "password does not match username"
            return  render_template("login.html", message=message)

        # Remember user who logged in
        session["teacher_id"] = teacher.teacher_id

        # Teacher can now start using the app
        return redirect("/teacher")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    """Log teacher out"""

    # Forget teacher's user ID or student's ID:
    session.clear()

    # Send teacher back to home page
    return redirect("/")


@app.route("/register", methods=["POST"])
def register():

    """Register a new user"""

    # Ensure user filled out form with all required information
    if not request.form.get("name"):
        message = "Please enter your full name"
        return render_template("login.html", message=message)
    if not request.form.get("username"):
        message = "Please choose a username"
        return render_template("login.html", message=message)
    if not request.form.get("password"):
        message = "please enter a password"
        return render_template("login.html", message=message)
    if not request.form.get("email"):
        message = "An email is required in order to register"
        return render_template("login.html", message=message)

    # Encrypt password
    hash = generate_password_hash(request.form.get("password"))

    # Add user to database, unless user already exists
    try:
        db.execute("INSERT INTO teachers (name, username, email, hash) VALUES (:name, :username, :email, :hash)",
            {"name":request.form.get("name"), "username":request.form.get("username"),
            "email":request.form.get("email"), "hash":hash})
        db.commit()
    except:
        message = "Username and/or email already exists"
        return render_template("login.html", message=message)

    # Log user in automatically after registering
    teacher = db.execute("SELECT * FROM teachers WHERE username = :username", {"username": request.form.get("username")}).fetchone()
    session["teacher_id"] = teacher.teacher_id

    # All is good, let user start searching for books
    return redirect('/teacher')



""" ******************* TEACHER GAME CREATION SECTION ********************** """

@app.route("/teacher")
@login_required
def teacher():

    """ This is the main page for the teacher to create games, add questions """

    # Query database for information to display on the main teachedr page
    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id = :teacherid", {"teacherid": session.get("teacher_id")}).fetchone()
    questions = db.execute("SELECT * FROM questions WHERE teacher = :teacher ORDER BY question_id", {"teacher": session.get("teacher_id")}).fetchall()
    games = db.execute("SELECT * FROM games WHERE teacher = :teacher ORDER BY game_id DESC", {"teacher": session.get("teacher_id")}).fetchall()

    return render_template("teacher.html", questions=questions, games=games, teacher=teacher)



@app.route("/create_new_game", methods=["POST"])
def create_new_game():

    """ Create a new game by supplying it's name, and a list of questions"""
    """ Questions can also be deleted here """

    # List of questions chosen
    question_list = []

    # Add all questions user chooses in form to this list as integers
    for i in request.form.getlist("questions"):
        question_list.append(int(i))

    if request.form.get("create_game"):
        if request.form.get("game_name") == "":
            flash("Please provide a name for your game", 'error')
            return redirect(url_for('teacher'))
        else:
            # Ensure teacher has not already created a game with that name
            games = db.execute("SELECT game_name FROM games WHERE teacher = :teacher", {"teacher": session.get("teacher_id")}).fetchall()
            for x in games:
                if x.game_name == request.form.get("game_name"):
                    flash("That name is being used already", 'error')
                    return redirect(url_for('teacher'))

            # Create game, add it to the database
            db.execute("INSERT INTO games (teacher, game_name, question_list) VALUES (:teacher, :game_name, :question_list)",
                       {"teacher":session.get("teacher_id"), "game_name":request.form.get("game_name"), "question_list":question_list})
            db.commit()

    if request.form.get("delete_question"):

        # Find out which games contain the questions to be deleted
        games_affected = db.execute("SELECT * FROM games WHERE question_list @> :question_list", {"question_list":question_list}).fetchall()

        # For each game, compare the list of questions to the list and remove them
        for game_affected in games_affected:
            new_question_list = game_affected.question_list.copy()
            for x in new_question_list:
                if x in question_list:
                    sys.stdout.write("Inside the loop")
                    new_question_list.remove(x)
            db.execute("UPDATE games SET question_list = :question_list WHERE game_name = :game_name", {"question_list":new_question_list, "game_name":game_affected.game_name})

        db.execute("DELETE FROM questions WHERE question_id = ANY(:question_list)", {"question_list":question_list})
        db.commit()

    return redirect("/teacher")


@app.route("/edit_game/<int:game_id>", methods=["GET", "POST"])
@login_required
def edit_game(game_id):

    """ Edit a game """

    game = db.execute("SELECT * FROM games WHERE game_id = :game_id", {"game_id":game_id}).fetchone()
    questions = db.execute("SELECT * FROM questions WHERE teacher = :teacher ORDER BY question_id", {"teacher":session.get("teacher_id")}).fetchall()
    teacher = db.execute("SELECT username FROM teachers WHERE teacher_id = :teacher_id", {"teacher_id":session.get("teacher_id")}).fetchone()

    print("YO?")

    # Add all questions user chooses in form to this list as integers
    question_list = []
    for i in request.form.getlist("questions"):
        question_list.append(int(i))

    if request.method == "POST":

        db.execute("UPDATE games SET game_name = :game_name, question_list = :question_list WHERE game_id = :game_id",
                    {"game_name":request.form.get("game_name"), "question_list":question_list, "game_id":game_id})
        db.commit()
        game = db.execute("SELECT * FROM games WHERE game_id = :game_id", {"game_id":game_id}).fetchone()

        return redirect("/game_control/" + teacher.username + "/" + game.game_name)

    question_list = game.question_list

    return render_template("edit_game.html", game=game, questions=questions, question_list=question_list)


@app.route("/add_new_question", methods=["POST"])
def add_new_question():
    """ Add new question to database which can be used in any game """

    # Insert question into database
    db.execute("INSERT INTO questions (teacher, question, choice_a, choice_b, choice_c, choice_d, answer) \
               VALUES (:teacher, :question, :choice_a, :choice_b, :choice_c, :choice_d, :answer)",
               {"teacher":session.get("teacher_id"),
               "question":request.form.get("question"),
               "choice_a":request.form.get("choice_a"),
               "choice_b":request.form.get("choice_b"),
               "choice_c":request.form.get("choice_c"),
               "choice_d":request.form.get("choice_d"),
               "answer":request.form.get("answer")})
    db.commit()

    return redirect("/teacher")


@app.route("/edit_question/<int:question_id>", methods=["GET", "POST"])
@login_required
def edit_question(question_id):

    """ Edit a question """

    question = db.execute("SELECT * FROM questions WHERE question_id = :question_id", {"question_id":question_id}).fetchone()

    if request.method == "POST":

        # Insert question into database
        db.execute("UPDATE questions SET question = :question, choice_a = :choice_a, choice_c = :choice_c, \
                    choice_d = :choice_d, answer = :answer WHERE question_id = :question_id",
                   {"question_id": question_id,
                   "question":request.form.get("question"),
                   "choice_a":request.form.get("choice_a"),
                   "choice_b":request.form.get("choice_b"),
                   "choice_c":request.form.get("choice_c"),
                   "choice_d":request.form.get("choice_d"),
                   "answer":request.form.get("answer")})
        db.commit()

        return redirect("/teacher")

    else:
        return render_template("question.html", question=question)


""" *************************** STUDENT VIEW ****************************** """

@app.route("/student")
def student():

    """ This is the main page for the student to create username and start play """

    # Check if student is already in database
    student = db.execute("SELECT * FROM students WHERE student_id = :student_id", {"student_id":session.get("student_id")}).fetchone()

    if student is None:
        # Student has been deleted, but session still exists, so clear it
        session.clear()
    else:
        # Student is still in session, and still playing - redirect to the game
        teacher = db.execute("SELECT * FROM teachers WHERE teacher_id = :teacher_id", {"teacher_id":student.students_teacher}).fetchone()
        return redirect("/game/" + teacher.username)

    # Get a list of all teachers for student to choose from (using typeahead)
    teachers = db.execute("SELECT * FROM teachers").fetchall()

    return render_template("student.html", teachers=teachers)


@app.route("/add_new_student", methods=["POST"])
def add_new_student():

    """ Add new student """

    teacher = db.execute("SELECT * FROM teachers WHERE username = :username", {"username":request.form.get("teacher")}).fetchone()

    db.execute("INSERT INTO students (student_name, students_teacher) VALUES (:student_name, :students_teacher)",
                {"student_name":request.form.get("student"), "students_teacher":teacher.teacher_id})
    db.commit()

    student = db.execute("SELECT * FROM students WHERE student_name = :student_name", {"student_name": request.form.get("student")}).fetchone()
    session["student_id"] = student.student_id

    # Redirect to the game page and teacher room
    game_url = "/game/" + request.form.get("teacher")

    return redirect(game_url)



""" *********************** GAME CONTROL AND PLAY ************************** """

@app.route("/game_control/<string:teacher>/<string:game_name>", methods=["GET", "POST"])
@login_required
def game_control(teacher, game_name):

    """ This view is where the teacher controls the game """

    # Query database for information to display on the game control page
    game = db.execute("SELECT * FROM games WHERE game_name = :game AND teacher = :teacher", {"game":game_name, "teacher":session.get("teacher_id")}).fetchone()
    questions = db.execute("SELECT * FROM questions WHERE question_id = ANY(:question_list) ORDER BY question_id", {"question_list":game.question_list}).fetchall()
    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id = :teacherid", {"teacherid": session.get("teacher_id")}).fetchone()
    students = db.execute("SELECT * FROM students WHERE students_teacher = :teacher", {"teacher": teacher.teacher_id}).fetchall()

    if request.form.get("action") == "play":
        db.execute("DELETE FROM students WHERE students_teacher = :students_teacher", {"students_teacher": teacher.teacher_id})
        db.execute("UPDATE games SET students = :students", {"students":[]})
        db.commit()

    if request.form.get("action") == "edit":
        return redirect("/edit_question")

    if request.form.get("action") == "delete":
        db.execute("DELETE FROM games WHERE teacher = :teacher AND game_name = :game_name", {"teacher":session.get("teacher_id"), "game_name":game_name})
        db.commit()
        return redirect("/teacher")

    # If teacher gets here via a get, and the game does not exist redirect them
    # back to the teacher page, otherwise add the game name to the active game
    if game is None:
        return redirect("/teacher")
    else:
        db.execute("UPDATE teachers SET active_game = :active_game WHERE teacher_id = :teacher_id", {"teacher_id": session.get("teacher_id"), "active_game":game_name})
        db.commit()
        teacher = db.execute("SELECT * FROM teachers WHERE teacher_id = :teacherid", {"teacherid": session.get("teacher_id")}).fetchone()

    return render_template("game_control.html", questions=questions, teacher=teacher, students=students)


@app.route("/game/<string:teacher>", methods=["GET", "POST"])
def game(teacher):

    """ This view controls what the student sees while playing the game"""

    game = ""
    correct = False
    question_number = 0
    question = None
    message = ""

    # Get the student if in session, otherwise redirect to student page to "log in"
    student = db.execute("SELECT * FROM students WHERE student_id = :student_id", {"student_id": session.get("student_id")}).fetchone()
    if student is None:
        return redirect("/student")

    # Create lists to temporarily hold student answer submissions
    questions_answered_list = student.questions_answered
    submitted_answers_list = student.submitted_answers
    results_list = student.results

    # Get teacher information that student selected
    teacher_selected = db.execute("SELECT * FROM teachers WHERE username = :username", {"username": teacher}).fetchone()

    # Students submits an answer through the form
    if request.method == 'POST':

        # Get the game that the teacher is transmitting
        game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name": teacher_selected.active_game}).fetchone()

        # Set the active game for the student
        db.execute("UPDATE students SET students_active_game = :students_active_game WHERE student_id = :student_id", {"student_id": session.get("student_id"), "students_active_game":game.game_name})
        db.commit()

        # Add student to the game
        student_list = game.students
        if student.student_id not in student_list:
            student_list.append(student.student_id)
            db.execute("UPDATE games SET students = :students WHERE game_id = :game_id", {"students": student_list, "game_id": game.game_id})
            db.commit()

        # Get the question student is answering from the form
        question_number = int(request.form.get("question_number"))
        question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":question_number}).fetchone()

        # Student has already submitted an answer to this question so:
        # Find position in list of the question that was already answered
        # then remove the question, answer, and result from the lists
        # so that they can be appended to without duplication
        if question_number in questions_answered_list:
            index = questions_answered_list.index(question_number)
            questions_answered_list.pop(index)
            submitted_answers_list.pop(index)
            results_list.pop(index)

        # Did the student get the answer correct?
        if request.form.get("submitted_answer") == question.answer:
            results_list.append(True)
        else:
            results_list.append(False)

        questions_answered_list.append(question_number)
        submitted_answers_list.append(request.form.get("submitted_answer"))

        db.execute("UPDATE students SET questions_answered = :questions_answered, submitted_answers = :submitted_answers, \
                    results = :results WHERE student_id = :student_id",
                    {"student_id": student.student_id, "questions_answered": questions_answered_list,
                    "submitted_answers": submitted_answers_list, "results": results_list})
        db.commit()

    return render_template("game.html", question=question, student=student, teacher=teacher, game=game, message=message)



""" *************************** SOCKET SECTION ****************************** """

# Server receives question sent by client
@socketio.on("play game")
def message(data):

    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id=:teacher_id", {"teacher_id":int(data['teacher_id'])}).fetchone()
    question = db.execute("SELECT * FROM questions WHERE question_id = :question_id", {"question_id": int(data['question_id'])}).fetchone()
    game = db.execute("SELECT * FROM games WHERE game_name = :game_name AND teacher = :teacher", {"game_name":data['game_name'], "teacher":teacher.teacher_id}).fetchone()

    message_for_students = {
        "question_id": question.question_id,
        "question": question.question,
        "choice_a": question.choice_a,
        "choice_b": question.choice_b,
        "choice_c": question.choice_c,
        "choice_d": question.choice_d,
        "game": game.game_name
    }

    # Teacher should also receive the answers so copy the dict and add it
    message = message_for_students.copy()
    message["answer"] = question.answer

    # Server sends client the data
    emit("question", message, room=teacher.username)
    emit("question for students", message_for_students, room=teacher.username)


# Server receives calculate results signal from teacher client
@socketio.on("calculate results")
def message(data):

    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id=:teacher_id", {"teacher_id": session.get("teacher_id")}).fetchone()
    game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name": teacher.active_game}).fetchone()
    students = db.execute("SELECT * FROM students WHERE students_teacher = :teacher_id", {"teacher_id":session.get("teacher_id")}).fetchall()

    for student in students:

        temp = student.questions_answered.copy()
        temp.sort()
        sorted_questions_answered = []
        sorted_submitted_answers = []
        sorted_results = []
        for i in range(len(temp)):
            index = student.questions_answered.index(temp[i])
            sorted_questions_answered.append(student.questions_answered[index])
            sorted_submitted_answers.append(student.submitted_answers[index])
            sorted_results.append(student.results[index])

        # Commit the sorted lists to the student's database
        db.execute("UPDATE students SET questions_answered = :questions_answered, submitted_answers = :submitted_answers, results = :results \
                    WHERE student_id = :student_id",
                    {"questions_answered":sorted_questions_answered, "submitted_answers":sorted_submitted_answers,
                    "results":sorted_results, "student_id":student.student_id})
        db.commit()

    # Server sends signal that game is over
    emit("show results", room=teacher.username)

# Server receives end game signal from client
@socketio.on("end game")
def message(data):

    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id=:teacher_id", {"teacher_id": session.get("teacher_id")}).fetchone()

    # Server sends signal that game is over
    emit("game over", room=teacher.username)

# Join a room
@socketio.on("join")
def message(data):
    join_room(data["room"])

    teacher = db.execute("SELECT * FROM teachers WHERE username = :username", {"username":data["room"]}).fetchone()

    if "student" in data:

        student = db.execute("SELECT * FROM students WHERE student_name = :student_name AND students_teacher = :students_teacher",
        {"student_name":data["student"], "students_teacher":teacher.teacher_id}).fetchone()

        # Show all logged in students to teacher
        emit("show students in room", data, room=data["room"])


# Student initiates a log out
@socketio.on('log student out')
def message(data):

    student = db.execute("SELECT * FROM students WHERE student_id = :student_id", {"student_id":session.get("student_id")}).fetchone()
    if student is not None:
        data["student"] = student.student_name
        data["leaving"] = True
        emit("show students in room", data, room=data["room"])
        game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name":student.students_active_game}).fetchone()

        if game is not None:
            students_in_game = game.students
            students_in_game.remove(student_to_be_deleted.student_id)
            db.execute("UPDATE games SET students = :students_in_game WHERE game_id = :game_id", {"students_in_game":students_in_game, "game_id":game.game_id})
            db.commit()

        # If it's a student, delete from databsase
        db.execute("DELETE from students WHERE student_id = :student_id", {"student_id":session.get("student_id")})
        db.commit()

    # Forget teacher's user ID or student's ID:
    session.clear()

    emit("student is out", data, room=data["room"])



@socketio.on("request teacher list")
def message():
    teacher_list = []
    teachers = db.execute("SELECT username FROM teachers").fetchall()
    for x in teachers:
        teacher_list.append(x.username)
    data = {"teachers":teacher_list}
    emit("teacher list", data)


@socketio.on("request student list")
def message(data):
    student_list = []
    teacher = db.execute("SELECT teacher_id FROM teachers WHERE username = :username", {"username":data["teacher"]}).fetchone()
    students = db.execute("SELECT student_name FROM students WHERE students_teacher = :teacher", {"teacher":teacher.teacher_id}).fetchall()
    for x in students:
        student_list.append(x.student_name)
    data = {"students":student_list}
    emit("student list", data)


""" **************************** SHOW RESULTS ****************************** """

@app.route("/results")
@login_required
def results():

    """Show teacher the results of all students who played the game"""

    # Query database for information to display in the results page
    teacher = db.execute("SELECT * FROM teachers WHERE teacher_id = :teacher_id", {"teacher_id": session.get("teacher_id")}).fetchone()
    game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name": teacher.active_game}).fetchone()
    students = db.execute("SELECT * FROM students WHERE students_teacher = :teacher_id", {"teacher_id":session.get("teacher_id")}).fetchall()

    # Creating lists and dicts of the information to display
    results_of_all_students = []
    student_results = {}

    # The list holding what the students submitted may be smaller than the number
    # of questions in the game.  A new list is therefore created to match the length
    # of the number of questions in the game, treating the questions student did
    # not answer as wrong (and NOT ANSWERED will be displayed)
    for x in students:
        temp_submitted_answers = x.submitted_answers.copy()
        temp_student_results = x.results.copy()

        student_results["students_name"] = x.student_name
        student_results["questions_in_game"] = game.question_list.copy()
        student_results["student_answers"] = ["NOT ANSWERED"] * len(game.question_list)
        student_results["student_results"] = [False] * len(game.question_list)
        student_results["score"] = 0

        for y in range(len(game.question_list)):
            if game.question_list[y] in x.questions_answered:
                student_results["student_answers"][y] = temp_submitted_answers.pop(0)
                student_results["student_results"][y] = temp_student_results.pop(0)

        # Figure out the students score
        score = 0
        for z in student_results["student_results"]:
            if z == True:
                score = score + 1
        student_results["score"] = round(100 * score / len(game.question_list))

        results_of_all_students.append(student_results.copy())

    return render_template("results.html", teacher=teacher, game=game, students=students, results=results_of_all_students, num_questions=len(game.question_list))


@app.route("/score")
def score():

    """Render student score page where student sees his/her results"""

    # Query database for information to display on student score page
    student = db.execute("SELECT * FROM students WHERE student_id = :student_id", {"student_id": session.get("student_id")}).fetchone()
    game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name":student.students_active_game}).fetchone()

    # Student is not in session
    if student is None:
        return redirect("/student")

    # Something went wrong, session lost its game information
    if game is None:
        return redirect("/end")

    questions = db.execute("SELECT * FROM questions WHERE question_id = ANY(:question_list)", {"question_list":game.question_list}).fetchall()

    results_list = []
    result = {}
    number_of_questions = len(game.question_list)
    correct = 0

    y = 0

    # Here I am creating a list of dicts that combine the question with the students
    # answers.  I think a postgres join would have been better, but not sure if
    # that works with arrays as references to other tables, so I made a copy
    for x in range(number_of_questions):
        result["question"] = questions[x].question
        result["choice_a"] = questions[x].choice_a
        result["choice_b"] = questions[x].choice_b
        result["choice_c"] = questions[x].choice_c
        result["choice_d"] = questions[x].choice_d
        result["answer"] = questions[x].answer
        if game.question_list[x] not in student.questions_answered:
            result["submitted_answer"] = "NOT ANSWERED"
            result["result"] = False
            y = y + 1
        else:
            result["submitted_answer"] = student.submitted_answers[x - y]
            result["result"] = student.results[x - y]
        results_list.append(result.copy())

    # Calculate student's score
    for x in student.results:
        if x:
            correct = correct + 1
    score = round(100 * correct / number_of_questions)

    return render_template("score.html", student=student, questions=questions, results_list=results_list, score=score, game=game)


""" **************************** END GAME ****************************** """

@app.route("/end_game_for_teacher")
def end_game_for_teacher():

    """Render end of game page for the teacher"""

    # Student scores are temporary and only valid until the end of the game
    db.execute("DELETE FROM students")

    # Inactivate the game for the teacher
    db.execute("UPDATE teachers SET active_game = :active_game WHERE teacher_id = :teacher_id", {"teacher_id": session.get("teacher_id"), "active_game":'No Game Being Played'})
    db.commit()

    # Erase students from game
    db.execute("UPDATE games SET students = :students WHERE teacher = :teacher", {"students": [], "teacher":session.get("teacher_id")})
    db.commit()

    return redirect("/teacher")


@app.route("/end")
def end_game():

    """Render end of game page for the students"""

    session.clear()

    return render_template("end.html")


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
