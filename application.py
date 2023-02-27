# Source code for myLedger
# Some inspiration was taken from cs50x's cs50.harvard.edu/x pset9/finance to very low extent

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology, value

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
    

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///database.db")

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
# For viewing index
def index():
    rows = db.execute("SELECT username FROM users WHERE id = ?", session['user_id'])
    username = rows[0]['username']
    return render_template("index.html", username=username)


@app.route("/login", methods=["GET", "POST"])
# For logging in
def login():
    session.clear()

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password"):
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
# For Logging out
def logout():

    session.clear()

    return redirect("/")
    

@app.route("/register", methods=["GET", "POST"])
# For Registering Users
def register():

    if request.method == "POST":

        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return apology("password and confirmation doesn't match", 400)
        pwdhash = generate_password_hash(password)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username already exists", 400)

        db.execute("INSERT INTO users (username , hash) VALUES(?, ?)", username, pwdhash)

        flash("Registered!")
        return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/password", methods=['GET', 'POST'])
@login_required
# For changing passwords
def passoword():
    if request.method == 'POST':

        if not request.form.get("current_password"):
            return apology("must provide password", 400)

        elif not request.form.get("new_password"):
            return apology("must provide new password", 400)

        elif not request.form.get("new_confirmation"):
            return apology("must provide confirmation for new password", 400)

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        new_confirmation = request.form.get("new_confirmation")
        if new_password != new_confirmation:
            return apology("New password and confirmation doesn't match", 400)

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        if not check_password_hash(rows[0]["hash"], current_password):
            return apology("invalid current password", 403)

        new_pwd_hash = generate_password_hash(new_password)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_pwd_hash, session["user_id"])
        flash("Password changed")
        return redirect("/")

    else:
        return render_template("password.html")


@app.route("/accounts", methods=["GET", "POST"])
@login_required
# for viewing current accounts for user
def accounts():
    data = db.execute("SELECT id, bank, currency, balance, status FROM accounts WHERE account_id = ?", session['user_id'])

    inventory = []
    total_worth = 0
    for row in data:
        currency = row["currency"]
        worth = float(row["balance"]) / float(value(currency))
        worth = round(worth, 2)
        total_worth = worth + total_worth
        inventory.append({
            "id": row["id"],
            "bank": row["bank"],
            "currency": currency,
            "balance": row["balance"],
            "worth": worth,
            "status": row["status"],
        })

        total_worth = round(total_worth, 2)
    return render_template("accounts.html", inventory=inventory, total_worth=total_worth)


@app.route("/transactions", methods=["GET", "POST"])
@login_required
# For viewing transaction history
def transactions():
    data = db.execute("SELECT id, title, amount, currency, bank, time FROM transactions WHERE transaction_id = ?", 
                      session["user_id"])
    return render_template("transactions.html", data=data)
    

@app.route("/payment", methods=["GET", "POST"])
@login_required
# For adding transactions
def payment():
    if request.method == "POST":

        if not request.form.get("title"):
            return apology("Must give purpose of debit", 400)
        if not request.form.get("amount"):
            return apology("Must give amount debited", 400)
        if not request.form.get("bank"):
            return apology("Must select bank used", 400)

        title = request.form.get("title")
        amount = int(request.form.get("amount"))
        bank = request.form.get("bank")
        rows = db.execute("SELECT currency, balance, status FROM accounts WHERE bank = ? AND account_id = ?", 
                          bank, session["user_id"])
        currency = rows[0]["currency"]
        balance = int(rows[0]["balance"])
        status = rows[0]["status"]

        if status == "blocked":
            flash("This account is blocked can't use for payments")
            return redirect("/accounts")
        else:
            if balance < amount:
                flash("Account has insufficient Funds!")
                return redirect("/accounts")
            else:
                new_balance = balance - amount

                db.execute("UPDATE accounts SET balance = ? WHERE bank = ? AND account_id = ?",
                           new_balance, bank, session["user_id"])

                db.execute("INSERT INTO transactions (transaction_id, title, amount, bank, currency) VALUES(?, ?, ?, ?, ?)",
                           session["user_id"], title, -1 * amount, bank, currency)

                if status == "inactive":
                    db.execute("UPDATE accounts SET status = ? WHERE bank = ? and account_id = ?",
                               "active", bank, session["user_id"])

                if new_balance <= 500:
                    flash(f"Transaction added! Account {bank} short on funds ")
                else:
                    flash("Transaction added")
                return redirect("/transactions")
    else:
        available_accounts = db.execute("SELECT bank FROM accounts WHERE account_id = ?", session["user_id"])
        return render_template("payment.html", available_accounts=available_accounts)


@app.route("/new", methods=["GET", "POST"])
@login_required
# For adding accounts for user
def new():
    if request.method == "POST":

        if not request.form.get("bank"):
            return apology("Must provide bank name", 400)
        if not request.form.get("currency"):
            return apology("Must provide Currency of Bank", 400)
        if not request.form.get("amount"):
            return apology("Must provide initial funds in account", 400)
        if not request.form.get("status"):
            return apology("Must provide status of bank account", 400)

        bank = request.form.get("bank")
        currency = request.form.get("currency")
        amount = float(request.form.get("amount"))
        status = request.form.get("status")

        rows = db.execute("SELECT * FROM accounts WHERE bank = ? AND account_id = ?", bank, session["user_id"])
        if len(rows) != 0:
            flash("Account already exists!")
            return redirect("/accounts")

        db.execute("INSERT INTO accounts (account_id, bank , currency, balance, status) VALUES(?, ?, ?, ?, ?)",
                   session['user_id'], bank, currency, amount, status)

        db.execute("INSERT INTO transactions (transaction_id, title, amount, currency, bank) VALUES(?, ?, ?, ?, ?)",
                   session["user_id"], "New Account Opened", +1 * amount, currency, bank)

        flash("Account Added!")

        return redirect("/accounts")

    else:
        currency = ['AED', 'AFN', 'ALL', 'AMD', 'ANG', 'AOA', 'ARS', 'AUD', 'AWG', 'AZN', 'BAM', 'BBD', 'BDT', 'BGN', 'BHD', 'BIF', 'BMD', 'BND',
                    'BOB', 'BRL', 'BSD', 'BTC', 'BTN', 'BWP', 'BYN', 'BZD', 'CAD', 'CDF', 'CHF', 'CLF', 'CLP', 'CNH', 'CNY', 'COP', 'CRC', 'CUC',
                    'CUP', 'CVE', 'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'EGP', 'ERN', 'ETB', 'EUR', 'FJD', 'FKP', 'GBP', 'GEL', 'GGP', 'GHS', 'GIP',
                    'GMD', 'GNF', 'GTQ', 'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'IMP', 'INR', 'IQD', 'IRR', 'ISK', 'JEP', 'JMD',
                    'JOD', 'JPY', 'KES', 'KGS', 'KHR', 'KMF', 'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD', 'LSL', 'LYD', 'MAD',
                    'MDL', 'MGA', 'MKD', 'MMK', 'MNT', 'MOP', 'MRU', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'MZN', 'NAD', 'NGN', 'NIO', 'NOK', 'NPR',
                    'NZD', 'OMR', 'PAB', 'PEN', 'PGK', 'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RSD', 'RUB', 'RWF', 'SAR', 'SBD', 'SCR', 'SDG',
                    'SEK', 'SGD', 'SHP', 'SLL', 'SOS', 'SRD', 'SSP', 'STD', 'STN', 'SVC', 'SYP', 'SZL', 'THB', 'TJS', 'TMT', 'TND', 'TOP', 'TRY',
                    'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'UZS', 'VEF', 'VES', 'VND', 'VUV', 'WST', 'XAF', 'XAG', 'XAU', 'XCD', 'XDR',
                    'XOF', 'XPD', 'XPF', 'XPT', 'YER', 'ZAR', 'ZMW', 'ZWL']
        return render_template("new.html", currency=currency)


@app.route("/funds", methods=["GET", "POST"])
@login_required
# For adding funds in an exisiting added account
def funds():
    if request.method == "POST":
        if not request.form.get("bank"):
            return apology("Must provide bank name", 400)
        if not request.form.get("funds"):
            return apology("Must provide the amount credited", 400)

        bank = request.form.get("bank")
        funds = int(request.form.get("funds"))
        rows = db.execute("SELECT balance, currency FROM accounts WHERE bank = ? AND account_id = ?", bank, session["user_id"])
        currency = rows[0]["currency"]
        balance = int(rows[0]["balance"])
        new_balance = balance + funds

        db.execute("UPDATE accounts SET balance = ?, status = ? WHERE bank = ? AND account_id = ?",
                   new_balance, "active", bank, session["user_id"])

        db.execute("INSERT INTO transactions (transaction_id, title, amount, currency, bank) VALUES(?, ?, ?, ?, ?)",
                   session["user_id"], "Money Credited", +1 * funds, currency, bank)

        flash("Credited!")
        return redirect("/accounts")

    else:
        available_accounts = db.execute("SELECT bank, currency FROM accounts WHERE account_id = ?", session["user_id"])
        return render_template("funds.html", available_accounts=available_accounts)