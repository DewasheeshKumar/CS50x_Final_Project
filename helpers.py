import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# Source cs50x's cs50.harvard.edu/x pset9/finance not my work all credits to cs50x's staff
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


# Source cs50x's cs50.harvard.edu/x pset9/finance not my work all credits to cs50x's staff
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Funtion to fetch the value of a currency with respect to USD inspiration taken from lookup() funtion in cs50x's cs50.harvard.edu/x pset9/finance
def value(symbol):

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return quote["rates"][f"{symbol}"]
    except (KeyError, TypeError, ValueError):
        return None
