import os

import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
 #   raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Home page (My Meals)
@app.route("/")
@login_required
def index():
    # This will get the current user id. It will then match that user id to the username by using select statement.
    # It will return the username of the current user based on id.
    id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", id)

    # The username will be stored in currentuser variable. User is a dictionary.
    currentuser = user[0]['username']

    # This will select all the columns and rows of the meals table where user2 is the currentuser and status is 2 which means the meal request was accepted. User2 is the receiving user of meal requests
    # so if the current user has meal request, their name should be in user2 and status should be 2 if they accepted that meal request.
    # This will use an or statement in the sql where statement. Or is used because the currentuser could possibly be user1 or user2. The currentuser
    # could be user2 because they received a meal request from another user; however, the currentuser can also be user1 because they may have been the one
    # who scheduled the meals.
    mymeals = db.execute("SELECT user1, type, time, date, restaurant, notes, id FROM meals WHERE (user2 = ? OR user1 = ?) AND status = ?", currentuser, currentuser, 2)
    return render_template("index.html", mymeals = mymeals)


# Login Page
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
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Logout Page
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id or the current user idea. It clears out the session.
    session.clear()

    # Redirect user to login form
    return redirect("/")


# Search Page - search for a user
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will check if the user put a username in the text field. If not, it will return an error.
        if not request.form.get("username"):
            flash('Must provide username')
            return redirect("/search")

        # This is the username that the current user is trying to search. This will display the searched user.
        suser = request.form.get("username")

        # This will retrieve all the usernames from the user table. This will be stored in a dictionary called allusers.
        # Allusers will be a dictionary of all the usernames in the users table. This will be used to check if that user exists in the for loop.
        allusers = db.execute("SELECT username from users")

        # This variable i will keep count of dictionary. It will be added in the for loop to indicate to move on to the next list
        # in the dictionary. This will be the counter.
        i = 0

        # This for loop will loop through the dictionary.
        for n in allusers:

            # This if statement will check if the username that was typed in is in the dictionary. If the username typed in the text field
            # is in the dictionary or in the table/list of usernames/registered users, then it will execute the next steps in the if statement
            # Anything out of this if statement means that the username typed in the text field does not exist.
            if suser == allusers[i]['username']:
                # This will grab all the information about the user selected. Then db execute will select all the information of the user typed in the text field or suser.
                userinfo = db.execute("SELECT username, name, email, phone, age, bio FROM users WHERE username = ?", suser)

                # This will return to a new page called search and pass the userinfo it got selected.
                return render_template("searched.html", userinfo=userinfo)

            # 1 is added each time so it will check the next list in the dictionary.
            i = i + 1

        # This means that the username does not exist so it will return with an apology saying the username does not exist.
        flash('Sorry this username does not exist')
        return redirect("/search")

    else:
        return render_template("search.html")


# Request page - you can send a friend request
@app.route("/request", methods=["GET", "POST"])
def frequest():
    if request.method == "POST":
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will check if the user put a username in the text field. If not, it will return an error.
        if not request.form.get("username"):
            flash('Please provide a username')
            return redirect("/request")

        # This is the username that the current user is trying to request to become friends. This is shortened for the requested user.
        ruser = request.form.get("username")

        # This will retrieve all the usernames from the user table. This will be stored in a dictionary called allusers.
        # Allusers will be a dictionary of all the usernames in the users table. This will be used to check if that user exists in the for loop.
        allusers = db.execute("SELECT username from users")

        # This variable i will keep count of dictionary. It will be added in the for loop to indicate to move on to the next list
        # in the dictionary. This will be the counter.
        i = 0
        # This for loop will loop through the dictionary.
        for n in allusers:

            # This will check if the user sends a friend request to themselves.
            if ruser == currentuser:
                flash("Sorry you can't send a friend request to yourself")
                return redirect("/request")

            # This if statement will check if the username that was typed in is in the dictionary. If the username typed in the text field
            # is in the dictionary or in the table/list of usernames/registered users, then it will execute the next steps in the if statement
            # Anything out of this if statement means that the username typed in the text field does not exist. If the username typed
            # by the user or in text field does not equal to at least on the registered users in the list of registered users then it will
            # that username does not exist.
            if ruser == allusers[i]['username']:
                # This will show the status that the current user and requested user is in. If they are friends it will return a 2, if the request is still
                # pending it will return a 0. This will be used to tell the user if they can send a friend request. This returns a list of the status.
                status = db.execute("SELECT status FROM ftable WHERE user1 = ? AND user2 = ?", currentuser, ruser)

                # This if statement will check the status. If the status dictionary is empty, then that means there is no
                # friend requests between the two users. That means there has been no friend requests ever sent from the current user to
                # the requested user. If there hasn't then, it will insert the friend request into the ftable and update the status.
                if len(status) == 0:
                    # This will insert the request in ftable and update status to pending then.
                    db.execute("INSERT INTO ftable(user1, user2, status) VALUES(?, ?, ?)", currentuser, request.form.get("username"), 0)
                    flash('Friend Request Sent')
                    return redirect("/friends")

                # This will return an integer to show the status of the two users. It will call on the status list. A 0 means pending, 1 is declined, 2 is accepted.
                # This will only run after it is confirmed that there has been no friend request made or the status dictionary is empty.
                currentstatus = status[0]['status']

                # This if statement will check if the current status is 0. If so, it will return an apology because that means there
                # has already been a pending request.
                if currentstatus == 0:
                    flash("You already sent a friend request and we are waiting on the other user")
                    return redirect("/request")

                # If the status is 2, that means the two users are alread friends. It will flash something to say they are already friends
                # then redirect them back to their friends page.
                if currentstatus == 2:
                    return redirect("/friends")

                # If the status is 1, then that means the requested user has already been declined to become friend. But this means that
                # the current user can request again which is why it will show another request on requested user.
                if currentstatus == 1:
                    db.execute("UPDATE ftable SET status = ? WHERE user1 = ? AND user2 = ?", 0, currentuser, ruser)
                    flash('Friend Request Sent')
                    return redirect("/")

            # 1 is added each time so it will check the next list in the dictionary.
            i = i + 1


        # This means that the username does not exist so it will return with an apology saying the username does not exist.
        flash('Sorry this user does not exist')
        return redirect("/request")

    else:
        return render_template("request.html")


# Friends Page - you can see who your current friends are
@app.route("/friends")
def friends():
    # This will get the current user id. It will then match that user id to the username by using select statement.
    # It will return the username of the current user based on id.
    id = session["user_id"]
    user = db.execute("SELECT username FROM users WHERE id = ?", id)

    # The username will be stored in currentuser variable. User is a dictionary.
    currentuser = user[0]['username']

    # This will use a db.execute statement to select all the rows in which the status is 2 which means they are accepted or
    # they are friends. A 2 means both users are friends. Friends will be stored as a dictionary.
    friends = db.execute("SELECT user1, user2 FROM ftable WHERE (user2 = ? OR user1 = ?) AND status = ?", currentuser, currentuser, 2)
    print(friends)

    # This empty list is to store the friends of the user.
    fuser = []

    # This is count for for loop
    i = 0

    # This for loop will loop through the friends list.
    for n in friends:
        # This if statement will check if the current username is equal to user1. If it is, then it would know user2 is their friend.
        # We are trying to display the username that is not the current user.
        if (friends[i]['user1'] == currentuser):
            fuser.append(friends[i]['user2'])
        if (friends[i]['user2'] == currentuser):
            fuser.append(friends[i]['user1'])
        i = i + 1

    # This will be used for the flask for loop, as we need to know length of the list.
    length = len(user)

    # This will render the html and pass on fuser list and length dictionary.
    return render_template("friends.html", fuser=fuser, length=length)

    # This will render the html and pass on friends dictionary.
    return render_template("friends.html", friends=friends)


# Friend Requests Page - you can see who sent you a friend request
@app.route("/friendrequest", methods=["GET", "POST"])
def friend_request():
    if request.method == "POST":
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will select all the rows in which the current user is user2. If the currentuser is user2, it means that someone or another
        # user requested them to be a friend. User2 of ftable is the receiver of the friend request. It will also only select where status is 0 which means pending.
        pending = db.execute("SELECT user1 FROM ftable WHERE user2 = ? AND status = ?", currentuser, 0)

        # This will assign fuser or friend user that the current user wants to accept or decline.
        fuser = request.form.get("username")

        # This is the counter for the for loop.
        i = 0

        # This for loop will loop through the dictionary of pending.
        for n in pending:
            # Similarly to the same logic as request. This if statement will check if fuser is in the list of pending or dictionary of pending.
            # The dictionary pending contains all the users friend request. Pending is a dictionary of all ther friend request that the user has.
            if fuser == pending[i]['user1']:
                # If the accept button is clicked, then the db.execute will update the status of both users to 2, which means they are friends. It will redirect to friends page.
                if request.form['submitbutton'] == 'accept':
                    db.execute("UPDATE ftable SET status = ? WHERE user1 = ? AND user2 = ?", 2, fuser, currentuser)
                    flash('Friend Request Accepted')
                    return redirect("/friends")

                # If the decline button is pressed, then db.execute will update status to 1, which means decline and redirect to friendrequest page.
                if request.form['submitbutton'] == 'decline':
                    db.execute("UPDATE ftable SET status = ? WHERE user1 = ? AND user2 = ?", 1, fuser, currentuser)
                    flash('Friend Request Declined')
                    return redirect("/friendrequest")

            # This will add to loop through.
            i = i + 1

        # This will return if the user types a username that is not in their friend requests.
        flash('Sorry this user is not on your friend requests')
        return redirect("/friendrequest")

    else:
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will select all the rows in which the current user is user2. If the currentuser is user2, it means that someone or another
        # user requested them to be a friend. User2 of ftable is the receiver of the friend request. It will also only select where status is 0 which means pending.
        pending = db.execute("SELECT user1 FROM ftable WHERE user2 = ? AND status = ?", currentuser, 0)

        # This will render template and pass pending.
        return render_template("friendrequest.html", pending=pending)


# Schedule Meal page - you can send a request to schedule a meal with another user on this page
@app.route("/schedulemeal", methods=["GET", "POST"])
def schedulemeal():
    if request.method == "POST":
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # The if statements below are to check the username, meal type, time, date, restaurant text fields are not left empty.
        # If any one of those fields are left empty when user press submits, it will pop up an apology or error telling them to fill it out.
        if not request.form.get("username"):
            flash('Please provide a username')
            return redirect("/schedulemeal")

        if not request.form.get("type"):
            flash('Please provide a meal type')
            return redirect("/schedulemeal")

        if not request.form.get("time"):
            flash('Please provide a meal time')
            return redirect("/schedulemeal")

        if not request.form.get("date"):
            flash('Please provide a date')
            return redirect("/schedulemeal")

        if not request.form.get("restaurant"):
            flash('Please provide a restaurant')
            return redirect("/schedulemeal")

        # This just assigns the user responses from the text fields into different variables.
        senduser = request.form.get("username")
        type = request.form.get("type")
        time = request.form.get("time")
        date = request.form.get("date")
        restaurant = request.form.get("restaurant")
        notes = request.form.get("notes")

        # This will retrieve all the usernames from the user table. This will be stored in a dictionary called allusers.
        # Allusers will be a dictionary of all the usernames in the users table. This will be used to check if that user exists in the for loop.
        allusers = db.execute("SELECT username from users")

        # This variable i will keep count of dictionary. It will be added in the for loop to indicate to move on to the next list
        # in the dictionary. This will be the counter.
        i = 0

        # This for loop will loop through the dictionary.
        for n in allusers:
            # This will check if the user sends a meal request to themselves.
            if senduser == currentuser:
                flash("Sorry you can't send a meal request to yourself")
                return redirect("/schedulemeal")

            # This if statement will check if the username that was typed in is in the dictionary. If the username typed in the text field
            # is in the dictionary or in the table/list of usernames/registered users, then it will execute the next steps.
            if senduser == allusers[i]['username']:

                # This will get all the ids from the current users' scheduled meals or requested meals.
                idlist = db.execute("SELECT id FROM meals WHERE user1 = ? AND user2 = ?", currentuser, senduser)

                # This will make sure that the user does not have more than 15 scheduled meals and requests at same time.
                if len(idlist) >= 15:
                    flash('Sorry you can only have a maximum of 15 scheduled meals and requests at a time')
                    return redirect("/schedulemeal")

                # This is used for the if statement so it runs true.
                t = 0
                # This while loop ensures that a new id is assigned to the meal request that the user sends.
                while t < 1:
                    # This creates a new number random from 1 to 15
                    id = random.randint(1,15)
                    # This if statement will check if this number is in the idlist. If not then we know this id number has not been used
                    # and it will be assigned to insertid
                    if id not in idlist:
                        insertid = id
                        t = t + 2

                # This will insert all the information from the user's meal request into the meals table including id.
                db.execute("INSERT INTO meals(user1, user2, type, time, date, restaurant, notes, status, id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", currentuser, senduser, type, time, date, restaurant, notes, 0, insertid)
                flash('Meal Request Sent')

                # This will return back to the home page which will show all the meals scheduled.
                return redirect("/")
            # 1 is added each time so it will check the next list in the dictionary.
            i = i + 1

        # This means that the username does not exist so it will return with an apology saying the username does not exist.
        flash('Sorry this user does not exist')
        return redirect("/schedulemeal")

    else:
        # This will render the page.
        return render_template("schedulemeal.html")


# Meal Request Page - you can see who sent a meal request to you and you can accept or decline the meal
@app.route("/mealrequests", methods=["GET", "POST"])
def meal_requests():
    if request.method == "POST":
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will provide a dictionary of a list of all the ids of the meals where the current user is the receiving user and the status is 0. The status of 0 means it is pending request.
        idlist = db.execute("SELECT id FROM meals WHERE user2 = ? AND status = ?", currentuser, 0)

        # Requested id. This stands for requested id and is the id that the user typed in that they want to accept or decline.
        rId = int(request.form.get("mealid"))


        i = 0
        # This for loop will loop through the dictionary of idlist. This for loop basically will make sure the rId or the id typed by the user
        # is a valid id. It will check in the idlist if that id typed by the user is an actual id. If not it will leave for loop and return apology.
        for n in idlist:

            # Similarly to the same logic as friend request. This if statement will check if rId is in the list of idlist or dictionary of idlist.
            # The dictionary idlist contains all the ids of the scheduled meals of the user. idlist is a dictionary of all of all the meals where the currentuser is the receiving user and status is 0.
            if rId == idlist[i]['id']:
                # If the accept button is clicked, then the db.execute will update the status of the meals table changing it to 2, which means they accepted the meals. It will redirect to meals page.
                if request.form['submitbutton'] == 'accept':
                    db.execute("UPDATE meals SET status = ? WHERE user2 = ? AND id = ?", 2, currentuser, rId)
                    flash('Meal Request Accepted')
                    return redirect("/")

                # If the decline button is pressed, then db.execute will delete the entire row or meal request, which means decline the meal and redirect to the meals page.
                # This will allow the id of that meal to be used again and it won't clutter the table with a bunch of declines.
                if request.form['submitbutton'] == 'decline':
                    db.execute("DELETE FROM meals WHERE user2 = ? AND id = ?", currentuser, rId)
                    flash('Meal Request Declined')
                    return redirect("/")

            # This will add to loop through.
            i = i + 1

        # This will return an apology page. This will only return once it is out of the for loop. It will return if the id typed is not an id on the meal requests.
        flash('Sorry that meal id is invalid')
        return redirect("/mealrequests")

    else:
        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]
        user = db.execute("SELECT username FROM users WHERE id = ?", id)

        # The username will be stored in currentuser variable. User is a dictionary.
        currentuser = user[0]['username']

        # This will select all the columns of the meals table where user2 is the currentuser and status is 0, which means the meal request is pending. User2 is the receiving user of meal requests
        # so if the current user has meal request, their name should be in user2 and status should be 0.
        pending = db.execute("SELECT user1, type, time, date, restaurant, notes, id FROM meals WHERE user2 = ? AND status = ?", currentuser, 0)

        # This will render template and pass pending.
        return render_template("mealrequests.html", pending=pending)


# Profile Page - you can update your profile for others to see
@app.route("/myprofile", methods=["GET", "POST"])
def myprofile():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # This will assign all the user input from the text fields into different variables. For example the name typed in the
        # name text field will be stored in the variable name.
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        age = request.form.get("age")
        bio = request.form.get("bio")

        # This will get the current user id. It will then match that user id to the username by using select statement.
        # It will return the username of the current user based on id.
        id = session["user_id"]

        # This will update the users table with the new information typed from above and the user input from myprofile page. Db execute will update it.
        db.execute("UPDATE users SET name = ?, email = ?, phone = ?, age = ?, bio = ? WHERE id = ?", name, email, phone, age, bio, id)
        flash('Profile Updated')
        return redirect("/")
    else:
        # This will render the template.
        return render_template("myprofile.html")


# Register Page - you can register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # This will ensure a username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # This will ensure a password was submitted
        elif not request.form.get("password"):
            return apology("Must provide a password", 400)

        # This will ensure the password typed and the password above matches each other
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Passwords must match", 400)

        # This will store the username to variable username.
        username = request.form.get("username")

        # This will create a hash password for the user typed password after it passes through the if statement of checking if both passwords match.
        newpassword = generate_password_hash(request.form.get("password"))

        # This will add the username, password which is hashed to the database. This will also check if the username exists in the database. If it does it will, return an apology it is taken.
        try:
            id = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, newpassword)
        except ValueError:
            return apology("username taken")

        # Redirect user to home page
        return redirect("/")

    # This will run when the GET method is used to open the page
    else:
        return render_template("register.html")


