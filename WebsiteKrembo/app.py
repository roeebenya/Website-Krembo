import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    # Execute the SQL query to sum up all donations
    result = db.execute("SELECT SUM(donation) FROM users")[0]['SUM(donation)']
    if result:
            result = result
    # Fetch the result
    else:
        result = 0
    totalDonations = result

    # Check if total_donations is not None (this can happen if there are no rows in the table)
    if totalDonations is None:
        totalDonations = 0

    return render_template("index.html", totalDonations = totalDonations)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
   # Clear the previous user_ids
    session.clear()
    if request.method == "GET":
          return render_template("register.html")


    # IF user submits form by POST
    if request.method == "POST":

        # Check that username submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Check that password submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Make sure password confirmation submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Make sure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
        try:
            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

            # Check if username already exists
            if len(rows) != 0:
                return apology("this username already exists", 400)

        except Exception as e:
        # Handle exception
            return str(e)
         # Insert new users into the database
        db.execute("INSERT INTO users (username, hash,donation ) VALUES(?, ?,0)",
                request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Query database for new user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user logged in
        session["user_id"] = rows[0]["user_id"]





        # Go back to home page
        return render_template("index.html")

@app.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    if request.method == "POST":
        try:
            donation_amount = float(request.form.get("amount"))
        except ValueError:
            return apology("Please provide a valid donation amount")
        try:
            donation_amount >0
        except:
            return apology("Please provide a valid donation amount")
        if donation_amount <= 0:
            return apology("Donation amount must be greater than 0")
        print(f"Received a donation of ${donation_amount:.2f}")
        username = request.form.get("username")
        usrchk = db.execute("SELECT user_id FROM users WHERE username = ?", username)
        if usrchk:
            usrchk = usrchk[0]['user_id']
        if usrchk != session['user_id']:
            return apology("Invalid username!! Try again")
        db.execute("UPDATE users SET donation = donation+? WHERE username = ?", donation_amount, request.form.get("username"))
        return redirect("/")
    else:
        return render_template("donate.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

@app.route("/programs", methods=["GET", "POST"])
def programs():
    return render_template("programs.html")

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

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
    return redirect("/login")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


