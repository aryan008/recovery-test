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
ATTRIBUTE_2_DICT ={"Not at all": 3,"Somewhat nutritious": 7, "Very nutritious": 10}
ATTRIBUTE_3_DICT ={"Yes - Tough session(s)": 5,"Yes - Light Session(s)": 10, "No": 15}
ATTRIBUTE_4_DICT ={"Less than 6 hours": 8,"6-7.5 hours": 17, "7.5+ hours": 25}
ATTRIBUTE_5_DICT ={"Exhausted/Tired": 3,"Ok": 7, "Good/Fresh": 10}
ATTRIBUTE_6_DICT ={"<1 Litre": 5,"1-3 Litres": 10, "3+ Litres": 15}
ATTRIBUTE_7_DICT ={"No": 3,"Yes - Less than 10 mins": 7, "Yes - More than 10 mins": 10}
ATTRIBUTE_8_DICT ={"No": 3,"Yes - Less than 10 mins": 7, "Yes - More than 10 mins": 10}

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
        result = get_result(username)
        date_entered = get_date(username)
        today = datetime.today().strftime('%Y-%m-%d')
        day_1 = datetime.strptime(date_entered, "%Y-%m-%d")
        day_2 = datetime.strptime(today, "%Y-%m-%d")

        
        # https://stackoverflow.com/questions/8419564/difference-between-two-dates-in-python
        date_difference = abs((day_1 - day_2).days)
        
        return render_template("profile.html", username=username, result=result, date_difference=date_difference, date_entered=date_entered)

    return redirect(url_for("login"))


@app.route("/delete_entry/<username>")
def delete_entry(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        latest_entry_delete = mongo.db.entries.find({"created_by": username}).sort(username, -1)  
        latest_delete = list(latest_entry_delete)
        last_entry_list = latest_delete[-1]
        last_entry_list_final = list(last_entry_list.items())
        final_delete = last_entry_list_final[1][1]
        delete_id = last_entry_list_final[0][1]
    
        mongo.db.entries.remove({"_id": delete_id})
        flash("Task Successfully Deleted!")
        return redirect(url_for("profile", username=username))



@app.route("/edit_entry/<username>", methods=["GET", "POST"])
def edit_entry(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        latest_entry_edit = mongo.db.entries.find({"created_by": username}).sort(username, -1)  
        latest_edit = list(latest_entry_edit)
        print(latest_edit)
        last_entry_list = latest_edit[-1]
        last_entry_list_final = list(last_entry_list.items())
        final_edit = last_entry_list_final[1][1]
        edit_id = last_entry_list_final[0][1]

        if request.method == "POST":
        
            result = get_result(username)

            final_attributes = request.form.getlist("options.choice")
            total = 0

            attr_1_query = final_attributes[0]
            attr_2_query = final_attributes[1]
            attr_3_query = final_attributes[2]
            attr_4_query = final_attributes[3]
            attr_5_query = final_attributes[4]
            attr_6_query = final_attributes[5]
            attr_7_query = final_attributes[6]
            attr_8_query = final_attributes[7]

            if attr_1_query == list(ATTRIBUTE_1_DICT.keys())[0]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[0]
            elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[1]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[1]
            elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[2]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[2]
            total += attr_1_result
            
            if attr_2_query == list(ATTRIBUTE_2_DICT.keys())[0]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[0]
            elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[1]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[1]
            elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[2]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[2]
            total += attr_2_result

            if attr_3_query == list(ATTRIBUTE_3_DICT.keys())[0]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[0]
            elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[1]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[1]
            elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[2]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[2]
            total += attr_3_result

            if attr_4_query == list(ATTRIBUTE_4_DICT.keys())[0]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[0]
            elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[1]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[1]
            elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[2]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[2]
            total += attr_4_result

            if attr_5_query == list(ATTRIBUTE_5_DICT.keys())[0]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[0]
            elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[1]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[1]
            elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[2]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[2]
            total += attr_5_result

            if attr_6_query == list(ATTRIBUTE_6_DICT.keys())[0]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[0]
            elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[1]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[1]
            elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[2]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[2]
            total += attr_6_result

            if attr_7_query == list(ATTRIBUTE_7_DICT.keys())[0]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[0]
            elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[1]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[1]
            elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[2]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[2]
            total += attr_7_result

            if attr_8_query == list(ATTRIBUTE_8_DICT.keys())[0]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[0]
            elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[1]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[1]
            elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[2]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[2]
            total += attr_8_result


            update = {
                "option_choice": request.form.getlist("options.choice"),
                "created_by": session["user"],
                "user_chosen_date": request.form.get("date_choice"),
                "submission_date": datetime.today().strftime('%Y-%m-%d'),
                "comment_text": request.form.get("comment_text"),
                "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                "score": total
            }
            mongo.db.entries.update({"_id": edit_id}, update)
            flash("Edit of entry successful!")
            return redirect(url_for("profile", username=username))
            
        options = mongo.db.recovery.find()
        return render_template("edit_entry.html", username=username, options=options)

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


@app.route("/new_entry/", methods=["GET", "POST"])
def new_entry():
    try:
        username = mongo.db.users.find_one(
                {"username": session["user"]})["username"]

        latest_entry_date = mongo.db.entries.find({"created_by": username}).sort(username, -1)
            
        initial_list_date = list(latest_entry_date)
        last_entry_date = initial_list_date[-1]
        last_entry_list_date = list(last_entry_date.items())
        final_date = last_entry_list_date[3][1]

        today = datetime.today().strftime('%Y-%m-%d')
        new_entry = datetime.strptime(final_date, "%Y-%m-%d")
        new_today = datetime.strptime(today, "%Y-%m-%d")

        # https://stackoverflow.com/questions/8419564/difference-between-two-dates-in-python
        date_difference = abs((new_today - new_entry).days)

        if date_difference !=0:
            if request.method == "POST":
                username = mongo.db.users.find_one(
                {"username": session["user"]})["username"]
                result = get_result(username)

                final_attributes = request.form.getlist("options.choice")
                total = 0

                attr_1_query = final_attributes[0]
                attr_2_query = final_attributes[1]
                attr_3_query = final_attributes[2]
                attr_4_query = final_attributes[3]
                attr_5_query = final_attributes[4]
                attr_6_query = final_attributes[5]
                attr_7_query = final_attributes[6]
                attr_8_query = final_attributes[7]

                if attr_1_query == list(ATTRIBUTE_1_DICT.keys())[0]:
                    attr_1_result = list(ATTRIBUTE_1_DICT.values())[0]
                elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[1]:
                    attr_1_result = list(ATTRIBUTE_1_DICT.values())[1]
                elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[2]:
                    attr_1_result = list(ATTRIBUTE_1_DICT.values())[2]
                total += attr_1_result
                
                if attr_2_query == list(ATTRIBUTE_2_DICT.keys())[0]:
                    attr_2_result = list(ATTRIBUTE_2_DICT.values())[0]
                elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[1]:
                    attr_2_result = list(ATTRIBUTE_2_DICT.values())[1]
                elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[2]:
                    attr_2_result = list(ATTRIBUTE_2_DICT.values())[2]
                total += attr_2_result

                if attr_3_query == list(ATTRIBUTE_3_DICT.keys())[0]:
                    attr_3_result = list(ATTRIBUTE_3_DICT.values())[0]
                elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[1]:
                    attr_3_result = list(ATTRIBUTE_3_DICT.values())[1]
                elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[2]:
                    attr_3_result = list(ATTRIBUTE_3_DICT.values())[2]
                total += attr_3_result

                if attr_4_query == list(ATTRIBUTE_4_DICT.keys())[0]:
                    attr_4_result = list(ATTRIBUTE_4_DICT.values())[0]
                elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[1]:
                    attr_4_result = list(ATTRIBUTE_4_DICT.values())[1]
                elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[2]:
                    attr_4_result = list(ATTRIBUTE_4_DICT.values())[2]
                total += attr_4_result

                if attr_5_query == list(ATTRIBUTE_5_DICT.keys())[0]:
                    attr_5_result = list(ATTRIBUTE_5_DICT.values())[0]
                elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[1]:
                    attr_5_result = list(ATTRIBUTE_5_DICT.values())[1]
                elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[2]:
                    attr_5_result = list(ATTRIBUTE_5_DICT.values())[2]
                total += attr_5_result

                if attr_6_query == list(ATTRIBUTE_6_DICT.keys())[0]:
                    attr_6_result = list(ATTRIBUTE_6_DICT.values())[0]
                elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[1]:
                    attr_6_result = list(ATTRIBUTE_6_DICT.values())[1]
                elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[2]:
                    attr_6_result = list(ATTRIBUTE_6_DICT.values())[2]
                total += attr_6_result

                if attr_7_query == list(ATTRIBUTE_7_DICT.keys())[0]:
                    attr_7_result = list(ATTRIBUTE_7_DICT.values())[0]
                elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[1]:
                    attr_7_result = list(ATTRIBUTE_7_DICT.values())[1]
                elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[2]:
                    attr_7_result = list(ATTRIBUTE_7_DICT.values())[2]
                total += attr_7_result

                if attr_8_query == list(ATTRIBUTE_8_DICT.keys())[0]:
                    attr_8_result = list(ATTRIBUTE_8_DICT.values())[0]
                elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[1]:
                    attr_8_result = list(ATTRIBUTE_8_DICT.values())[1]
                elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[2]:
                    attr_8_result = list(ATTRIBUTE_8_DICT.values())[2]
                total += attr_8_result


                entry = {
                    "option_choice": request.form.getlist("options.choice"),
                    "created_by": session["user"],
                    "user_chosen_date": request.form.get("date_choice"),
                    "submission_date": datetime.today().strftime('%Y-%m-%d'),
                    "comment_text": request.form.get("comment_text"),
                    "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                    "score": total
                }
                mongo.db.entries.insert_one(entry)
                flash("Task Successfully Added")
                return redirect(url_for("profile", username=username))
            
            options = mongo.db.recovery.find()
            return render_template("new_entry.html", options = options, date_difference=date_difference)

        else:
            flash("Task Already Added")
            return redirect(url_for("profile", username=username))

    except IndexError as error:
        if request.method == "POST":
            username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
            result = get_result(username)

            final_attributes = request.form.getlist("options.choice")
            total = 0

            attr_1_query = final_attributes[0]
            attr_2_query = final_attributes[1]
            attr_3_query = final_attributes[2]
            attr_4_query = final_attributes[3]
            attr_5_query = final_attributes[4]
            attr_6_query = final_attributes[5]
            attr_7_query = final_attributes[6]
            attr_8_query = final_attributes[7]

            if attr_1_query == list(ATTRIBUTE_1_DICT.keys())[0]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[0]
            elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[1]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[1]
            elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[2]:
                attr_1_result = list(ATTRIBUTE_1_DICT.values())[2]
            total += attr_1_result
            
            if attr_2_query == list(ATTRIBUTE_2_DICT.keys())[0]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[0]
            elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[1]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[1]
            elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[2]:
                attr_2_result = list(ATTRIBUTE_2_DICT.values())[2]
            total += attr_2_result

            if attr_3_query == list(ATTRIBUTE_3_DICT.keys())[0]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[0]
            elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[1]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[1]
            elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[2]:
                attr_3_result = list(ATTRIBUTE_3_DICT.values())[2]
            total += attr_3_result

            if attr_4_query == list(ATTRIBUTE_4_DICT.keys())[0]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[0]
            elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[1]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[1]
            elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[2]:
                attr_4_result = list(ATTRIBUTE_4_DICT.values())[2]
            total += attr_4_result

            if attr_5_query == list(ATTRIBUTE_5_DICT.keys())[0]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[0]
            elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[1]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[1]
            elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[2]:
                attr_5_result = list(ATTRIBUTE_5_DICT.values())[2]
            total += attr_5_result

            if attr_6_query == list(ATTRIBUTE_6_DICT.keys())[0]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[0]
            elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[1]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[1]
            elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[2]:
                attr_6_result = list(ATTRIBUTE_6_DICT.values())[2]
            total += attr_6_result

            if attr_7_query == list(ATTRIBUTE_7_DICT.keys())[0]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[0]
            elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[1]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[1]
            elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[2]:
                attr_7_result = list(ATTRIBUTE_7_DICT.values())[2]
            total += attr_7_result

            if attr_8_query == list(ATTRIBUTE_8_DICT.keys())[0]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[0]
            elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[1]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[1]
            elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[2]:
                attr_8_result = list(ATTRIBUTE_8_DICT.values())[2]
            total += attr_8_result


            entry = {
                "option_choice": request.form.getlist("options.choice"),
                "created_by": session["user"],
                "user_chosen_date": request.form.get("date_choice"),
                "submission_date": datetime.today().strftime('%Y-%m-%d'),
                "comment_text": request.form.get("comment_text"),
                "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                "score": total
            }
            mongo.db.entries.insert_one(entry)
            flash("Task Successfully Added")
            return redirect(url_for("profile", username=username))

        options = mongo.db.recovery.find()
        return render_template("new_entry.html", options = options)


@app.route("/all_entries")
def all_entries():
    username = mongo.db.users.find_one({"username": session["user"]})

    if session['user']:
        full_entries = mongo.db.entries.find()
        full_entries_list = list(full_entries)

        # https://www.programiz.com/python-programming/methods/list/reverse
        reversed_list = full_entries_list.reverse()
        
    return render_template("all_entries.html", full_entries_list=full_entries_list)


@app.route("/manage_users/", methods=["GET", "POST"])
def manage_users():
    username = mongo.db.users.find_one({"username": session["user"]})
    # Only admin can access this page
    if session['user'] == 'admin':
        full_users = mongo.db.users.find()
        full_users_list = list(full_users)
        
    return render_template("manage_users.html", full_users_list=full_users_list)


@app.route("/delete_user", methods=["GET", "POST"])
def delete_user():
    username = mongo.db.users.find_one({"username": session["user"]})
    # Only admin can access this page
    if session['user'] == "admin":
        mongo.db.entries.remove({"created_by": username})
        flash("Removal done")
        return redirect(url_for("login"))


def get_date(username):
    try:
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        latest_entry_date = mongo.db.entries.find({"created_by": username}).sort(username, -1)
        
        initial_list_date = list(latest_entry_date)
        last_entry_date = initial_list_date[-1]
        last_entry_list_date = list(last_entry_date.items())
        final_date = last_entry_list_date[3][1]
        return final_date
    
    except IndexError as error:
        todays_date = datetime.today().strftime('%Y-%m-%d')
        return todays_date


def get_result(username):
    try:
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        latest_entry = mongo.db.entries.find({"created_by": username}).sort(username, -1)
        
        initial_list = list(latest_entry)
        last_entry = initial_list[-1]
        
        last_entry_list = list(last_entry.items())
        final_attributes = last_entry_list[1][1]

        total = 0

        attr_1_query = final_attributes[0]
        attr_2_query = final_attributes[1]
        attr_3_query = final_attributes[2]
        attr_4_query = final_attributes[3]
        attr_5_query = final_attributes[4]
        attr_6_query = final_attributes[5]
        attr_7_query = final_attributes[6]
        attr_8_query = final_attributes[7]

        if attr_1_query == list(ATTRIBUTE_1_DICT.keys())[0]:
            attr_1_result = list(ATTRIBUTE_1_DICT.values())[0]
        elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[1]:
            attr_1_result = list(ATTRIBUTE_1_DICT.values())[1]
        elif attr_1_query == list(ATTRIBUTE_1_DICT.keys())[2]:
            attr_1_result = list(ATTRIBUTE_1_DICT.values())[2]
        total += attr_1_result
        
        if attr_2_query == list(ATTRIBUTE_2_DICT.keys())[0]:
            attr_2_result = list(ATTRIBUTE_2_DICT.values())[0]
        elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[1]:
            attr_2_result = list(ATTRIBUTE_2_DICT.values())[1]
        elif attr_2_query == list(ATTRIBUTE_2_DICT.keys())[2]:
            attr_2_result = list(ATTRIBUTE_2_DICT.values())[2]
        total += attr_2_result

        if attr_3_query == list(ATTRIBUTE_3_DICT.keys())[0]:
            attr_3_result = list(ATTRIBUTE_3_DICT.values())[0]
        elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[1]:
            attr_3_result = list(ATTRIBUTE_3_DICT.values())[1]
        elif attr_3_query == list(ATTRIBUTE_3_DICT.keys())[2]:
            attr_3_result = list(ATTRIBUTE_3_DICT.values())[2]
        total += attr_3_result

        if attr_4_query == list(ATTRIBUTE_4_DICT.keys())[0]:
            attr_4_result = list(ATTRIBUTE_4_DICT.values())[0]
        elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[1]:
            attr_4_result = list(ATTRIBUTE_4_DICT.values())[1]
        elif attr_4_query == list(ATTRIBUTE_4_DICT.keys())[2]:
            attr_4_result = list(ATTRIBUTE_4_DICT.values())[2]
        total += attr_4_result

        if attr_5_query == list(ATTRIBUTE_5_DICT.keys())[0]:
            attr_5_result = list(ATTRIBUTE_5_DICT.values())[0]
        elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[1]:
            attr_5_result = list(ATTRIBUTE_5_DICT.values())[1]
        elif attr_5_query == list(ATTRIBUTE_5_DICT.keys())[2]:
            attr_5_result = list(ATTRIBUTE_5_DICT.values())[2]
        total += attr_5_result

        if attr_6_query == list(ATTRIBUTE_6_DICT.keys())[0]:
            attr_6_result = list(ATTRIBUTE_6_DICT.values())[0]
        elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[1]:
            attr_6_result = list(ATTRIBUTE_6_DICT.values())[1]
        elif attr_6_query == list(ATTRIBUTE_6_DICT.keys())[2]:
            attr_6_result = list(ATTRIBUTE_6_DICT.values())[2]
        total += attr_6_result

        if attr_7_query == list(ATTRIBUTE_7_DICT.keys())[0]:
            attr_7_result = list(ATTRIBUTE_7_DICT.values())[0]
        elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[1]:
            attr_7_result = list(ATTRIBUTE_7_DICT.values())[1]
        elif attr_7_query == list(ATTRIBUTE_7_DICT.keys())[2]:
            attr_7_result = list(ATTRIBUTE_7_DICT.values())[2]
        total += attr_7_result

        if attr_8_query == list(ATTRIBUTE_8_DICT.keys())[0]:
            attr_8_result = list(ATTRIBUTE_8_DICT.values())[0]
        elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[1]:
            attr_8_result = list(ATTRIBUTE_8_DICT.values())[1]
        elif attr_8_query == list(ATTRIBUTE_8_DICT.keys())[2]:
            attr_8_result = list(ATTRIBUTE_8_DICT.values())[2]
        total += attr_8_result    
        
        return total

    except IndexError as error:
        narrative = "No entry yet, please submit one"
        return narrative


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
