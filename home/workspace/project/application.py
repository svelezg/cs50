import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from random import shuffle
from helpers import apology, login_required, lookup, message


# Configure application
app = Flask(__name__)

UPLOAD_FOLDER = os.path.normpath('static/uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///orchid.db")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure selection was made
        if not request.form.get("selection"):
            return apology("must select a genera", 400)

        # Query users database for active contribution
        act = db.execute("SELECT active FROM users WHERE id = :id", id=id)
        active = act[0]["active"]

        selection = request.form.get("selection")
        # Query contributions database for genera
        cont = db.execute("SELECT * FROM contributions WHERE id_contribution = :id_contribution AND genera= :genera",
                          id_contribution=active,
                          genera=selection)
        if len(cont) != 0:
            value = 10
            type = "Correct"

        else:
            value = 0
            type = "Wrong"

        db.execute(
            """INSERT INTO "activities"(id,id_contribution,type,points, genera)
            VALUES(:id, :id_contribution, :type, :points, :genera)""",
            id=session["user_id"],
            id_contribution=active,
            genera=selection,
            type=type,
            points=value)

        db.execute(
            """UPDATE "users" SET points = points + :value WHERE id = :id""",
            value=value,
            id=id)

        return redirect("/")


# User reached route via GET (clicking link)
    else:
        # from contribution - played random select
        answer = db.execute(
            """SELECT * FROM contributions WHERE id_contribution IN (SELECT id_contribution FROM contributions ORDER BY RANDOM() LIMIT 1)""")
        for answer in answer:
            id_contribution = answer["id_contribution"]
            file_name = answer["file_name"]
            gen = answer["genera"]
            genera_pair = {'genera': gen}
            contributor = answer["id"]

        # Query users database for contributor username
        user_contributor = db.execute("SELECT username FROM users WHERE id = :id", id=contributor)
        user = user_contributor[0]["username"]

        # Remember id_contribution
        db.execute(
            """UPDATE "users" SET active = :value WHERE id = :id""", value=id_contribution, id=id)

        # select 3 random genera from genera database to complete 4 answer options
        options = []
        options = db.execute(
            """SELECT genera FROM genera WHERE id_genera IN (SELECT id_genera FROM genera ORDER BY RANDOM() LIMIT 3)""")
        options.append(genera_pair)
        shuffle(options)

        return render_template("index.html", genera=gen, options=options,
                               file_name=file_name, id_contribution=id_contribution, user=user)


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    user_dat = db.execute("SELECT * FROM users WHERE username =:username", username=username)

    if len(username) > 1 and len(user_dat) != 0:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/check_genera", methods=["GET"])
def check_genera():
    """Return true if genera is in database, else false, in JSON format"""
    genera = request.args.get("genera")
    genera_dat = db.execute("SELECT * FROM genera WHERE genera =:genera", genera=genera)

    if len(genera) > 1 and len(genera_dat) != 0:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/activity")
@login_required
def activity():
    """Show user activity"""

    id = session["user_id"]
    plays = []
    plays = db.execute("SELECT * FROM activities WHERE id = :id", id=session['user_id'])
    username = db.execute("SELECT username FROM users WHERE id = :id", id=session['user_id'])
    name = (username[0]['username'])

    for play in plays:
        play["date"] = str(play["timestamp"])
        play["genera"] = str(play["genera"])
        play["points"] = int(play["points"])
        play["type"] = str(play["type"])

    p = db.execute("SELECT points FROM users WHERE id = :id", id=session['user_id'])
    for p in p:
        points = str(p["points"])

    return render_template("activity.html", name=name, plays=plays, points=points)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username does not already exist
        if len(rows) != 0:
            return apology("username already exist", 400)

        # Generate password hash
        hash = generate_password_hash(request.form.get("password"))

        # Insert USER into database
        db.execute(
            """INSERT INTO users(username,hash)
            VALUES(:username, :hash)""",
            username=request.form.get("username"),
            hash=hash)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=["GET", "POST"])
def upload_file():

    if request.method == "POST":

        # Ensure file was submitted
        if not request.files['image']:
            return apology("must provide file", 400)

        # Ensure genera was submitted
        elif not request.form.get("genera"):
            return apology("must provide genera", 400)

        gen = request.form.get("genera")
        genera_dat = db.execute("SELECT * FROM genera WHERE genera =:genera", genera=gen)

        if len(gen) > 1 and len(genera_dat) != 0:
            genera = gen
        else:
            return apology("Non valid genera", 400)

        file = request.files['image']
        id = session["user_id"]

        if file and allowed_file(file.filename) and genera:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

            db.execute(
                """INSERT INTO "contributions"(file_name,id,genera)
                    VALUES(:file_name, :id, :genera)""",
                file_name=filename,
                id=session["user_id"],
                genera=genera)

            return message('Thanks a lot for your contribution!', file_name=filename)

    else:
        return render_template("upload.html")


@app.route('/play', methods=["GET"])
def play():

    return redirect("/",)


@app.route("/test", methods=["GET"])
@login_required
def test():
    id = session["user_id"]

    # Query users database for active contribution
    act = db.execute("SELECT active FROM users WHERE id = :id", id=id)
    active = act[0]["active"]

    selection = request.args.get("genera")

    cont = db.execute("SELECT * FROM contributions WHERE id_contribution = :id_contribution AND genera= :genera",
                      id_contribution=active,
                      genera=selection)
    if len(cont) != 0:
        return jsonify(True)

    else:
        return jsonify(False)


@app.route("/contributions")
@login_required
def contributions():
    """Show list of contributions"""

    plays = []
    plays = db.execute("SELECT *, count(genera) FROM contributions GROUP BY genera ORDER BY count(genera) DESC")
    for play in plays:
        play["genera"] = str(play["genera"])
        play["id"] = str(play["count(genera)"])

    totals = []
    totals = db.execute("SELECT *, count(*) FROM contributions")

    for total in totals:
        total["count"] = str(total["count(*)"])

    return render_template("contributions.html", plays=plays, total=total)

