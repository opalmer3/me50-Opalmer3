import os
import requests
import urllib.parse

from flask import Flask, session, redirect, render_template, request, jsonify
from flask_session import Session
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

# DATABASE_URL=postgres://wgfjftevfzhdct:89abb1c9f9fe4dd0c6e447c1baa97cd91387d5f8185681a77a137aea5123002f@ec2-54-247-72-30.eu-west-1.compute.amazonaws.com:5432/dtec51jksolrh
app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Configure session to use filesystem
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Define login required decorated_function
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# # Api key
KEY = "ccARhB9p9gbTKj4NhzoBgQ"


@app.route("/")
def index():
    return render_template("search.html")

@app.route("/logout")
def logout():
    # clear user date
    session.clear()

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # for redirecting back to page where they logged in
        next_url = request.form.get("url")

        # Check fields not empty
        if not username:
            message="Please enter your username"
            # In the event of an error send the user back to the page they came from, by default assume the login came from the login page
            if not next_url:
                return render_template("login.html", message=message)
            else:
                return redirect(next_url + "&msg=" + message)

        if not password:
            message="Please enter your password"
            # In the event of an error send the user back to the page they came from, by default assume the login came from the login page
            if not next_url:
                return render_template("login.html", message=message)
            else:
                return redirect(next_url + "&msg=" + message)

        # Query db for username
        rows = db.execute("SELECT * from users WHERE username = :username", {"username": username}).fetchall()

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            message = "Invalid username or password"
            # In the event of an error send the user back to the page they came from, by default assume the login came from the login page
            if not next_url:
                return render_template("login.html", message=message)
            else:
                return redirect(next_url + "&msg=" + message)

        # Remember which user has logged in
        session["user_id"] = rows[0]["userid"]

        # if user logged in via log in page redirect to search. If they logged in from another page redirect back to that page.
        if not next_url:
            return redirect("/search")
        else:
            return redirect(next_url)

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    # if method=post then form submitted
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

            # Check fields not empty and passwords match
        if not name or not username or not email or not password or not confirm:
            message = "Please fill out all fields"
            return render_template("register.html", message=message)

        if password != confirm:
            message = "Passwords do not match"
            return render_template("register.html", message=message)

            # Check if username available
        rows = db.execute("SELECT * from users WHERE username= :username", {"username": username}).fetchall()
        if len(rows) !=0:
            message="Username unavailable"
            return render_template("register.html", message=message)
        # Check if email already used
        rows = db.execute("SELECT * from users WHERE email= :email", {"email": email}).fetchall()
        if len(rows) !=0:
            message="Account already registered under this email"
            return render_template("register.html", message=message)

        # Input user data into db and redirect to login page
        try:
            db.execute("INSERT INTO users (name, username, email, hash) VALUES(:name, :username, :email, :hash)",
                    {"name": name, "username":username, "email": email, "hash": generate_password_hash(password)})
            db.commit()
        except:
            message="Error updating database"
            return render_template("register.html", message=message)
        return redirect("/login")

        # else we arrived here via get request
    else:
        return render_template("register.html")

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
    if len(rows) >= 1 or len(username) < 1:
        return jsonify(False)
    else:
        return jsonify(True)



@app.route("/search", methods=["GET"])
def search():
    if not request.args.get("query"):
        return render_template("search.html")
    rawinput = request.args.get("query")
    input = rawinput.replace("'", "")
    input = "'%" + input + "%'"

    dbquery =  "SELECT * from books WHERE isbn LIKE "  + input +  " OR title LIKE " + input + " OR author LIKE " + input + " ORDER BY title ASC"

    rows = db.execute(dbquery).fetchall()

    if len(rows) == 0:
        message = "No matching books"
        return render_template("search.html", message=message)

    return render_template("search.html", rows=rows)



@app.route("/book", methods=["GET"])
def book ():
    isbn = request.args.get("isbn")
    # Get error message if being redirected from submitreview route
    msg=request.args.get("msg")

    rows = db.execute("SELECT books.isbn, title, author, year, reviews.text, reviews.userid, reviews.rating FROM books LEFT JOIN reviews ON reviews.isbn = books.isbn WHERE books.isbn = :isbn", {"isbn": isbn}).fetchall()

    if (len(rows) == 0):
        return render_template("search.html")

    # set a dummy value in first list item because loop.index in jinja begins at 1 not 0.
    usernames = ["n/a"]
    for row in rows:
        if row.text:
        # Select username from db save as a list and pass to page.
            username = db.execute("SELECT username FROM users WHERE userid = :userid", {"userid": row.userid}).fetchone()
            usernames.append(username[0])

    # Send request to goodbooks api
    res = {'books': ['hi', 'you']} # requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    res = res.json()

    if msg != None:
        return render_template("book.html", rows=rows, usernames=usernames, message=msg, res=res)

    return render_template("book.html", rows=rows, usernames=usernames, res=res)

@app.route("/submitreview", methods=["GET"])
@login_required
def submitreview():
    text = request.args.get("text")
    isbn = request.args.get("isbn")
    rating = request.args.get("rating")

    if rating == 0:
        message="The minimum rating is 0.1"
        return redirect("/book?isbn=" + isbn + "&msg=" + message)

    if len(text) < 100:
        message="Please write at least 100 characters"
        return redirect("/book?isbn=" + isbn + "&msg=" + message)

    rows = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

    # Check user hasnt already submitted a review for the book
    rows1 = db.execute("SELECT * FROM reviews WHERE userid = :userid AND isbn = :isbn", {"userid": session["user_id"], "isbn": isbn}).fetchall()

    if len(rows1) != 0:
        message="You have already submitted a review for this book"
        return redirect("/book?isbn=" + isbn + "&msg=" + message)
    try:
        db.execute("INSERT INTO reviews (userid, isbn, text, rating) VALUES(:userid, :isbn, :text, :rating)",
                {"userid": session["user_id"], "isbn": isbn, "text": text, "rating": rating})
        db.commit()
        return redirect("/book?isbn=" + isbn)
    except:
        message= "Sorry, we could not process your review at this time. Please try again later."
        return redirect("/book?isbn=" + isbn + "&msg=" + message)

@app.route("/api/<string:isbn>")
def api(isbn):
        # Query database
        try:
            review_rows = db.execute("SELECT AVG(CAST(rating AS float)), COUNT(isbn) FROM reviews WHERE isbn = :isbn", {'isbn': isbn}).fetchone()
            books_rows = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        except:
            code= "404"
            message="We could not process your request at this time, please try again later"
            return render_template("error.html", code=code, message=message)
        if len(books_rows) == 0:
            code = "404"
            message="This book is not in our database"
            return render_template("error.html", code=code, message=message)
        # return response if success
        response = {'title': books_rows['title'], 'author': books_rows['author'], 'year': books_rows['year'], 'average_rating': review_rows[0], 'review_count': review_rows[1]}
        return jsonify(response)
