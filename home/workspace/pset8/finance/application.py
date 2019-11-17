import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    id = session["user_id"]
    stocks = []
    stocks = db.execute(
        """SELECT symbol, SUM(shares) as s_shares FROM portfolio WHERE id = :id GROUP BY symbol ORDER BY symbol""", id=session['user_id'])
    username = db.execute("SELECT username FROM users WHERE id = :id", id=session['user_id'])
    name = (username[0]['username'])

    total_val = 0

    for stock in stocks:
        symbol = str(stock["symbol"])
        shares = int(stock["s_shares"])
        quote = lookup(symbol)
        stock["company"] = (quote['name'])
        stock["price"] = (quote['price'])
        stock["value"] = (stock["price"] * shares)
        total_val += stock["value"]

    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])
    total_cash = float(cash[0]['cash'])

    total = total_val + total_cash

    return render_template("index.html", name=name, balance=total_cash, total=total, stocks=stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol exist
        elif not lookup(request.form.get("symbol")):
            return apology("symbol is not valid", 400)

        # Ensure shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("number of shares must be a positive integer", 400)

        if shares < 1:
            return apology("number of shares must be a positive integer", 400)

        sym = request.form.get("symbol")
        quote = lookup(sym)
        symbol = quote['symbol']
        name = quote['name']
        price = quote['price']

        value = shares * quote["price"]
        id = session["user_id"]

        cash = db.execute(
            """SELECT cash FROM users WHERE id = :id""", id=session['user_id'])
        # Query database for user's cash
        if not cash or float(cash[0]["cash"]) < price * shares:
            return apology("Not enought balance for purchase", 403)

        else:
            db.execute(
                """INSERT INTO "purchases"(id,symbol,price,amount)
            VALUES(:id, :symbol, :price, :amount)""",
                id=session["user_id"],
                symbol=symbol,
                price=price,
                amount=shares)

            db.execute(
                """UPDATE "users" SET cash = cash - :value WHERE id = id""",
                value=value)

            rows = db.execute("SELECT * FROM portfolio WHERE id = :id AND symbol = :symbol",
                              id=session["user_id"],
                              symbol=symbol)

            if len(rows) != 0:
                #stock_id = rows[0]["stock_id"]
                db.execute(
                    """UPDATE "portfolio" SET shares = shares + :amount WHERE id = :id AND symbol = :symbol""",
                    amount=shares,
                    id=session["user_id"],
                    symbol=symbol)

            else:
                db.execute(
                    """INSERT INTO "portfolio"(id,symbol,shares)
                    VALUES(:id, :symbol, :amount)""",
                    id=session["user_id"],
                    symbol=symbol,
                    amount=shares)

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    user_dat = db.execute("SELECT * FROM users WHERE username =:username", username=username)

    if len(username) > 1 and len(user_dat) != 0:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    id = session["user_id"]
    stocks = []
    stocks = db.execute("SELECT * FROM purchases WHERE id = :id", id=session['user_id'])
    username = db.execute("SELECT username FROM users WHERE id = :id", id=session['user_id'])
    name = (username[0]['username'])

    for stock in stocks:
        stock["date"] = str(stock["Timestamp"])
        symbol = str(stock["symbol"])
        stock["shares"] = int(stock["amount"])
        quote = lookup(symbol)
        stock["company"] = (quote['name'])
        """stock["price"] = (quote['price'])"""
        stock["value"] = (stock["price"] * stock["shares"])
        if stock["shares"] > 0:
            stock["transaction"] = "Purchase"
        else:
            stock["transaction"] = "Sell"

    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])
    total_cash = float(cash[0]['cash'])

    return render_template("history.html", name=name, stocks=stocks)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol exist
        elif not lookup(request.form.get("symbol")):
            return apology("symbol is not valid", 400)

        sym = request.form.get("symbol")
        quote = lookup(sym)
        symbol = quote['symbol']
        name = quote['name']
        price = quote['price']

        return render_template("quoted.html", symbol=symbol, name=name, price=price)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


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


@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    """Add money to the account or cash out"""

    username = db.execute("SELECT username FROM users WHERE id = :id", id=session['user_id'])
    name = (username[0]['username'])

    cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
    balance = int(cash[0]["cash"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        try:
            amount = float(request.form.get("amount"))
        except ValueError:
            return apology("investment or chash out must be positive", 400)

        # Ensure amount was submitted and is positive
        if not request.form.get("amount") or amount < 1:
            return apology("investment or chash out must be positive", 400)

        # Ensure transaction was chosen
        elif not (request.form.get("transaction")):
            return apology("Must specify transaction", 400)

        else:

            transaction = request.form.get("transaction")

            if transaction == "cash_out":
                if balance < amount:
                    return apology("Your balance is less than the selected amount", 400)

                else:
                    db.execute(
                        """UPDATE "users" SET cash = cash - :value WHERE id = :id""",
                        value=amount,
                        id=session['user_id'])

            else:
                db.execute(
                    """UPDATE "users" SET cash = cash + :value WHERE id = :id""",
                    value=amount,
                    id=session['user_id'])

        return redirect("/cash")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("cash.html", name=name, balance=balance)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via POST (as by submitting a form via POST)

    stocks = db.execute("SELECT symbol FROM portfolio WHERE id = :id",
                       id=session["user_id"])

    if request.method == "POST":

        # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol exist
        elif not lookup(request.form.get("symbol")):
            return apology("symbol is not valid", 400)

        shares = int(request.form.get("shares"))
        # Ensure shares is a positive integer

        if shares < 1:
            return apology("number of shares must be positive", 400)
        sym = request.form.get("symbol")
        quote = lookup(sym)
        symbol = quote['symbol']
        name = quote['name']
        price = quote['price']

        value = shares * quote["price"]
        id = session["user_id"]
        sec = db.execute("SELECT * FROM portfolio WHERE id = :id AND symbol = :symbol",
                         id=session["user_id"],
                         symbol=symbol)

        if not(sec[0]["symbol"]):
            return apology("You do not own these securities", 400)

        elif sec[0]["shares"] < shares:
            return apology("You are trying to sell more shares than what you own", 400)

        else:
            db.execute(
                """INSERT INTO "purchases"(id,symbol,price,amount)
                VALUES(:id, :symbol, :price, :amount)""",
                id=session["user_id"],
                symbol=symbol,
                price=price,
                amount=-shares)

            db.execute(
                """UPDATE "users" SET cash = cash + :value WHERE id = id""",
                value=value)

            selection = db.execute("SELECT stock_id, shares FROM portfolio WHERE id = :id AND symbol = :symbol",
                                   id=session["user_id"],
                                   symbol=symbol)

            erase = selection[0]["stock_id"]
            shares_b = selection[0]["shares"] - shares

            if shares_b == 0:
                #db.execute("DELETE FROM portfolio WHERE symbol=:symbol AND id=:id", id=session["user_id"], symbol=symbol)
                db.execute("DELETE FROM portfolio WHERE stock_id=:stock_id", stock_id=erase)

            else:
                db.execute(
                    """UPDATE "portfolio" SET shares = shares - :amount WHERE id = :id AND symbol = :symbol""",
                    amount=shares,
                    id=session["user_id"],
                    symbol=symbol)

            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("sell.html", stocks=stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
