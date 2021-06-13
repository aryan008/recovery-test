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
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

ATTRIBUTE_1_DICT ={"No": 2,"Yes - Pool": 3, "Yes - Ice Bath/Sea Swim": 5}
ATTRIBUTE_2_SCORE = [3,7,10]
ATTRIBUTE_3_SCORE = [5,10,15]
ATTRIBUTE_4_SCORE = [8,17,25]
ATTRIBUTE_5_SCORE = [3,7,10]
ATTRIBUTE_6_SCORE = [5,10,15]
ATTRIBUTE_7_SCORE = [3,7,10]
ATTRIBUTE_8_SCORE = [3,7,10]

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
        flash("Registration Successful! {}, thanks for joining the team.".format(request.form.get("username")))
        return redirect(url_for("create_account"))
        return redirect(url_for("profile", username=session["user"]))

    return render_template("create_account.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/about")
def about():
    data = []
    with open("data/attributes.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("about.html", attribute_json=data)


@app.route("/new_entry", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        entry = {
            "option_choice": request.form.getlist("options.choice"),
            "created_by": session["user"],
            "submission_date": datetime.today().strftime('%Y-%m-%d')
        }
        mongo.db.entries.insert_one(entry)
        flash("Task Successfully Added")
        return redirect(url_for("new_entry"))

    options = mongo.db.recovery.find()
    return render_template("new_entry.html", options = options)


def get_result():
    # https://stackoverflow.com/questions/10920651/get-the-latest-record-from-mongodb-collection
    latest_entry = mongo.db.entries.find_one( {"$query":{}, "$orderby":{"$natural":-1}} )
    full_pycache = list(latest_entry.items())
    selection_list = full_pycache[1][1]
    attr_1_query = selection_list[0]
    attr_2_query = selection_list[1]

    if attr_1_query == list(ATTRIBUTE_1_DICT.keys())[0]:
        attr_1_result = list(ATTRIBUTE_1_DICT.values())[0]
    elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[1]:
        attr_1_result = list(ATTRIBUTE_1_DICT.values())[1]
    elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[2]:
        attr_1_result = list(ATTRIBUTE_1_DICT.values())[2]
    
    if attr_2_query == "Not at all":
        attr_2_result = 3
    elif attr_2_query == "Somewhat nutritious":
        attr_2_result = 7
    elif attr_2_query == "Very nutritious":
        attr_2_result = 10
    
    print(attr_1_result)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

