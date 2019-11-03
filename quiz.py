import os
import requests

from flask import Flask, render_template, request, redirect, session, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from functools import wraps

# This looks for secret stuff in a .env file
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Check for environment variable
if not os.getenv("QUIZDB_URL"):
    raise RuntimeError("QUIZDB_URL is not set")

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

# Setup database connection
engine = create_engine(os.getenv("QUIZDB_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("userid") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():

    """Render home page"""

    return render_template("index.html")


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
        user = db.execute("SELECT * FROM users WHERE username = :username",
            {"username":request.form.get("username")}).fetchone()

        # Is username in database?
        if not user:
            message = "username does not exist"
            return  render_template("login.html", message=message)

        # Does password match username?
        if not check_password_hash(user.hash, request.form.get("password")):
            message = "password does not match username"
            return  render_template("login.html", message=message)

        # Remember user who logged in
        session["userid"] = user.user_id

        # Begin searching for books
        return redirect("/teacher")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():

    """Log user out"""

    # Forget user # ID:
    session.clear()

    # Send user back to home page
    return redirect("/login")


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
        db.execute("INSERT INTO users (name, username, email, hash) VALUES (:name, :username, :email, :hash)",
            {"name":request.form.get("name"), "username":request.form.get("username"),
            "email":request.form.get("email"), "hash":hash})
        db.commit()
    except:
        message = "Username and/or email already exists"
        return render_template("login.html", message=message)

    # Log user in automatically after registering
    user = db.execute("SELECT * FROM users WHERE username = :username", {"username": request.form.get("username")}).fetchone()
    session["userid"] = user.user_id

    # All is good, let user start searching for books
    return redirect('/teacher')


@app.route("/create_new_game", methods=["POST"])
def create_new_game():

    question_list = []

    for i in request.form.getlist("questions"):
        question_list.append(int(i))

    db.execute("INSERT INTO games (teacher, game_name, question_list) VALUES (:teacher, :game_name, :question_list)",
               {"teacher":"uziel", "game_name":request.form.get("game_name"), "question_list":question_list})
    db.commit()
    game = db.execute("SELECT * FROM games WHERE game_name = :game_name", {"game_name":request.form.get("game_name")}).fetchone()

    return redirect("/teacher")

@app.route("/add_new_question", methods=["POST"])
def add_new_question():
    db.execute("INSERT INTO questions (question, choice_a, choice_b, choice_c, choice_d, answer) \
               VALUES (:question, :choice_a, :choice_b, :choice_c, :choice_d, :answer)",
               {"question":request.form.get("question"),
               "choice_a":request.form.get("choice_a"),
               "choice_b":request.form.get("choice_b"),
               "choice_c":request.form.get("choice_c"),
               "choice_d":request.form.get("choice_d"),
               "answer":request.form.get("answer")})
    db.commit()
    return redirect("/teacher")

@app.route("/teacher")
@login_required
def teacher():
    print("PPPPPPPPPPPPPPPPPPPPPPPPPPPP")
    print(session["userid"])
    questions = db.execute("SELECT * FROM questions").fetchall()
    games = db.execute("SELECT * FROM games").fetchall()
    # Get user information to send back to the search page
    user = db.execute("SELECT * FROM users WHERE user_id = :userid", {"userid": session["userid"]}).fetchone()
    return render_template("teacher.html", questions=questions, games=games, user=user)

@app.route("/game/<string:teacher>/<string:game_name>", methods=["GET", "POST"])
def game(teacher, game_name):

    result = ""
    correct = False
    question_number = 0

    game = db.execute("SELECT * FROM games WHERE game_name = :game AND teacher = :teacher", {"game":game_name, "teacher":"uziel"}).fetchone()

    question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()

    if request.method == 'POST':
        question_number = game.question_list.index(int(request.form.get("question_number")))
        question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()
        if request.form.get("submitted_answer") == question.answer:
            result = "Correct!!!"
        else:
            result = "Sorry!"
        question_number = game.question_list.index(int(request.form.get("question_number"))) + 1

    question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()

    questions = db.execute("SELECT * FROM questions WHERE question_id = ANY(:question_list)", {"question_list":game.question_list}).fetchall()

    #user = db.execute("SELECT * FROM users WHERE username = :username", {"username": "raphaeluziel"}).fetchone()
    #print(user)
    try:
        user = db.execute("SELECT * FROM users WHERE user_id = :userid", {"userid": session["userid"]}).fetchone()
    except:
        user = None

    return render_template("game.html", game=game, question=question, questions=questions, result=result, user=user)

@app.route("/game_control/<string:teacher>/<string:game_name>", methods=["GET", "POST"])
def game_control(teacher, game_name):

    result = ""
    correct = False
    question_number = 0

    game = db.execute("SELECT * FROM games WHERE game_name = :game AND teacher = :teacher", {"game":game_name, "teacher":"uziel"}).fetchone()

    question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()

    if request.method == 'POST':
        question_number = game.question_list.index(int(request.form.get("question_number")))
        question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()
        if request.form.get("submitted_answer") == question.answer:
            result = "Correct!!!"
        else:
            result = "Sorry!"
        question_number = game.question_list.index(int(request.form.get("question_number"))) + 1

    question = db.execute("SELECT * FROM questions WHERE question_id =:question_number", {"question_number":game.question_list[question_number]}).fetchone()

    questions = db.execute("SELECT * FROM questions WHERE question_id = ANY(:question_list)", {"question_list":game.question_list}).fetchall()

    #user = db.execute("SELECT * FROM users WHERE username = :username", {"username": "raphaeluziel"}).fetchone()
    #print(user)
    try:
        user = db.execute("SELECT * FROM users WHERE user_id = :userid", {"userid": session["userid"]}).fetchone()
    except:
        user = None

    return render_template("game_control.html", game=game, question=question, questions=questions, result=result, user=user)

# Server receives message sent by client
@socketio.on("start game")
def message(data):
    print(data)
    question = db.execute("SELECT * FROM questions WHERE question_id = 1").fetchone()
    message = {
        "question": question.question,
        "choice_a": question.choice_a,
        "choice_b": question.choice_b,
        "choice_c": question.choice_c,
        "choice_d": question.choice_d
    }

    # Server sends client the data
    emit("push question", message, broadcast=True)



if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0')
