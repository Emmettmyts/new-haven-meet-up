import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Apology Page - This will return an apology if something goes wrong
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

    # This will return the template for apology which is a picture with error and code.
    return render_template("apology.html", top=code, bottom=escape(message)), code


# This is to ensure that the user has logged in.
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This if statement will see if the user_id is none then it will redirect back to the login page. If the user hasn't registered, it will redirect to login.
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    # This will return the decorated_function
    return decorated_function


