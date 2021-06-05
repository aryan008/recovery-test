# pip3 install Flask, pip3 install flask-pymongo, pip3 install dnspython
# touch env.py

""" import os
os.environ.setdefault("IP", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("SECRET_KEY", "xtJ)ux}K6I|macPC,*dkT8:A}5>e-<")
os.environ.setdefault("MONGO_URI", "mongodb+srv://root:rOOtUser@myfirstcluster.lkzob.mongodb.net/recovery_test?retryWrites=true&w=majority")
os.environ.setdefault("MONGO_DBNAME", "recovery_test") """

import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_recovery")
def get_recovery():
    recovery = mongo.db.recovery.find()
    return render_template("recovery.html", recovery=recovery)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists! Please choose another.")
            return redirect(url_for("create_account"))

        # else statement on truthy
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("create_account"))

    return render_template("create_account.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
