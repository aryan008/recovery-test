# pip3 install Flask, pip3 install flask-pymongo, pip3 install dnspython
# touch env.py

""" import os
os.environ.setdefault("IP", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("SECRET_KEY", "xtJ)ux}K6I|macPC,*dkT8:A}5>e-<")
os.environ.setdefault("MONGO_URI", "mongodb+srv://root:rOOtUser@myfirstcluster.lkzob.mongodb.net/recovery_test?retryWrites=true&w=majority")
os.environ.setdefault("MONGO_DBNAME", "recovery_test") """

# Import necessary libraries
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, abort)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# Initialise flask and wire up Mongo DB
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# Create the eight dictionaries that house the user form response scoring
ATTRIBUTE_1_DICT ={"No": 2,"Yes - Pool": 3, "Yes - Ice Bath/Sea Swim": 5}
ATTRIBUTE_2_DICT ={"Not at all": 3,"Somewhat nutritious": 7, "Very nutritious": 10}
ATTRIBUTE_3_DICT ={"Yes - Tough session(s)": 5,"Yes - Light Session(s)": 10, "No": 15}
ATTRIBUTE_4_DICT ={"Less than 6 hours": 8,"6-7.5 hours": 17, "7.5+ hours": 25}
ATTRIBUTE_5_DICT ={"Exhausted/Tired": 3,"Ok": 7, "Good/Fresh": 10}
ATTRIBUTE_6_DICT ={"<1 Litre": 5,"1-3 Litres": 10, "3+ Litres": 15}
ATTRIBUTE_7_DICT ={"No": 3,"Yes - Less than 10 mins": 7, "Yes - More than 10 mins": 10}
ATTRIBUTE_8_DICT ={"No": 3,"Yes - Less than 10 mins": 7, "Yes - More than 10 mins": 10}

mongo = PyMongo(app)


# Route for the home page
@app.route("/get_recovery")
def get_recovery():
    # Get the recovery collection from Mongo DB
    recovery = mongo.db.recovery.find()
    # Try statement to determine if the user is in session
    try:
        if session["user"]:
            user_check = "Yes"

        else:
            user_check = "No"

    # If no user is in session
    except KeyError as error:
        user_check = "No"

    # Render template with appropriate variables
    return render_template("recovery.html", recovery=recovery, user_check=user_check)


# Route for the create account page
@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # if the username has already been created, redirect and flash message
        if existing_user:
            flash("Username already exists! Please choose another.")
            return redirect(url_for("create_account"))

        # else statement on truthy to register the user and store in Mongo DB
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie with a welcome message and redirect to their profile
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful! {}, thanks for joining the team.".format(request.form.get("username")))
        return redirect(url_for("profile", username=session["user"]))

    return render_template("create_account.html")


# Route for the login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # if the username is on the DB
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


# Route for the profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # if the user is in session
    if session["user"]:
        # call the get_result() & get_date() functions
        result = get_result(username)
        date_entered = get_date(username)
        today = datetime.today().strftime('%Y-%m-%d')
        day_1 = datetime.strptime(date_entered, "%Y-%m-%d")
        day_2 = datetime.strptime(today, "%Y-%m-%d")

        
        # https://stackoverflow.com/questions/8419564/difference-between-two-dates-in-python
        # get the date difference between today and last entry
        date_difference = abs((day_1 - day_2).days)
        
        return render_template("profile.html", username=username, result=result, date_difference=date_difference, date_entered=date_entered)

    else:
        abort(404)


# Route for the user to delete their own individual profile
@app.route("/delete_user_user/<username>", methods=["GET", "POST"])
def delete_user_user(username):
    # grab the user's username
    username_user = mongo.db.users.find_one({"username": session["user"]})
    
    if session['user']:
        # remove the users account from the DB and all the entries they have made
        mongo.db.users.remove({"username": username})
        mongo.db.entries.remove({"created_by": username})
        session.pop("user")
        flash("Profile Deleted!")
        return redirect(url_for("create_account"))

    else:
        abort(404)


# Route for the user to update their password
@app.route("/password_update", methods=["GET", "POST"])
def password_update():
    if request.method == "POST":
        # find the user's current password
        old_password = mongo.db.users.find_one(
            {"username": session["user"]})["password"]

        # if statement that checks if the entered password matches their stored password
        if check_password_hash(old_password, request.form.get("old_password")):
            # update the users password on the database
            mongo.db.users.update_one(
                {"username": session["user"]},
                {"$set": {"password": generate_password_hash(
                    request.form.get("newpassword"))}})
            flash("Password Successfully updated")
            return redirect(url_for("get_recovery"))
        # if password entered doesn't match
        else:
            flash("Password is incorrect, please try again")
            return redirect(url_for("pw_change"))

    return render_template("pw_change.html")


# Route for the user to delete their entry for the day
@app.route("/delete_entry/<username>")
def delete_entry(username):
    # find the users username
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # if the user is in session
    if session["user"]:
        # find that user's latest entry
        latest_entry_delete = mongo.db.entries.find({"created_by": username}).sort(username, -1)  
        latest_delete = list(latest_entry_delete)
        last_entry_list = latest_delete[-1]
        last_entry_list_final = list(last_entry_list.items())
        # Below and above code to grab the _id of the users latest entry
        final_delete = last_entry_list_final[1][1]
        delete_id = last_entry_list_final[0][1]
    
        # remove this entry from the database
        mongo.db.entries.remove({"_id": delete_id})
        flash("Entry Successfully Deleted!")
        return redirect(url_for("profile", username=username))

    else:
        abort(404)


# Route for the user to edit their entry for the day
@app.route("/edit_entry/<username>", methods=["GET", "POST"])
def edit_entry(username):
    # find the users username
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    # if the user is in session
    if session["user"]:
        # find that user's latest entry
        latest_entry_edit = mongo.db.entries.find({"created_by": username}).sort(username, -1)  
        latest_edit = list(latest_entry_edit)
        last_entry_list = latest_edit[-1]
        last_entry_list_final = list(last_entry_list.items())
        final_edit = last_entry_list_final[1][1]
        edit_id = last_entry_list_final[0][1]
        # above code used to grab the _id of the users latest entry

        # once the user updates their entry
        if request.method == "POST":
            # call the get_result() function
            result = get_result(username)

            # grab the user's form choices from the entry form
            final_attributes = request.form.getlist("options.choice")
            # start the total counter
            total = 0

            # Note that the score calculation/attribute querying is compliant with the DRY principle.
            # Despite the formulae looking similar for the edit_entry, new_entry & get_result sections of
            # this file, based on varying factors they are pulling different stored dictionary information to get
            # the necessary attributes selected 
            # set up the attribute queries to get each individual response
            attr_1_query = final_attributes[0]
            attr_2_query = final_attributes[1]
            attr_3_query = final_attributes[2]
            attr_4_query = final_attributes[3]
            attr_5_query = final_attributes[4]
            attr_6_query = final_attributes[5]
            attr_7_query = final_attributes[6]
            attr_8_query = final_attributes[7]

            # The below if statements match the user's responses on an 
            # attribute-by-attribute basis and get the correct values from the constant dictionaries.
            # The resulting score is then added to the above total counter
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

            # a dictionary is created based on the users form choices to update the entry
            update = {
                "option_choice": request.form.getlist("options.choice"),
                "created_by": session["user"],
                "user_chosen_date": request.form.get("date_choice"),
                "submission_date": datetime.today().strftime('%Y-%m-%d'),
                "comment_text": request.form.get("comment_text"),
                "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                "score": total
            }
            # update the Mongo DB with the users entry
            mongo.db.entries.update({"_id": edit_id}, update)
            flash("Edit of entry successful!")
            return redirect(url_for("profile", username=username))

        # the options to populate the form are grabbed from Mongo DB    
        options = mongo.db.recovery.find()
        return render_template("edit_entry.html", username=username, options=options)

    else:
        abort(404)


# Route for the user to log out of their profile
@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Route for the user to view the about page
@app.route("/about")
def about():
    # create an empty list called data
    data = []
    # with statement to get the JSON file information and load into the data list
    with open("data/attributes.json", "r") as json_data:
        data = json.load(json_data)
    return render_template("about.html", attribute_json=data)


# Route for the user to make a new entry
@app.route("/new_entry/", methods=["GET", "POST"])
def new_entry():
    # Try statement to grab the users last entry
    # This is necessary as the user may not have any entries yet
    try:
        # grab the username from the DB
        username = mongo.db.users.find_one(
                {"username": session["user"]})["username"]

        # find the users latest entry
        latest_entry_date = mongo.db.entries.find({"created_by": username}).sort(username, -1)

        # get the date of the last entry of the user    
        initial_list_date = list(latest_entry_date)
        last_entry_date = initial_list_date[-1]
        last_entry_list_date = list(last_entry_date.items())
        final_date = last_entry_list_date[3][1]

        # get todays date and format the same as the last entry date
        today = datetime.today().strftime('%Y-%m-%d')
        new_entry = datetime.strptime(final_date, "%Y-%m-%d")
        new_today = datetime.strptime(today, "%Y-%m-%d")

        # https://stackoverflow.com/questions/8419564/difference-between-two-dates-in-python
        # get the date difference between today and last entry
        date_difference = abs((new_today - new_entry).days)

        # if this date difference is not zero
        if date_difference !=0:
            # if the user posts
            if request.method == "POST":
                # grab the username
                username = mongo.db.users.find_one(
                {"username": session["user"]})["username"]

                # call the get_result() function
                result = get_result(username)

                # get the choices entered by the user
                final_attributes = request.form.getlist("options.choice")
                # start the total counter
                total = 0

                # set up the attribute queries to get each individual response
                # Note that the score calculation/attribute querying is compliant with the DRY principle.
                # Despite the formulae looking similar for the edit_entry, new_entry & get_result sections of
                # this file, based on varying factors they are pulling different stored dictionary information to get
                # the necessary attributes selected
                attr_1_query = final_attributes[0]
                attr_2_query = final_attributes[1]
                attr_3_query = final_attributes[2]
                attr_4_query = final_attributes[3]
                attr_5_query = final_attributes[4]
                attr_6_query = final_attributes[5]
                attr_7_query = final_attributes[6]
                attr_8_query = final_attributes[7]

                # The below if statements match the user's responses on an 
                # attribute-by-attribute basis and get the correct values from the constant dictionaries.
                # The resulting score is then added to the above total counter
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

                # a dictionary is created based on the users form choices to create the entry
                entry = {
                    "option_choice": request.form.getlist("options.choice"),
                    "created_by": session["user"],
                    "user_chosen_date": request.form.get("date_choice"),
                    "submission_date": datetime.today().strftime('%Y-%m-%d'),
                    "comment_text": request.form.get("comment_text"),
                    "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                    "score": total
                }
                # insert the entry into the database
                mongo.db.entries.insert_one(entry)
                flash("Entry Successfully Added")
                return redirect(url_for("profile", username=username))
            
            # grab the form options from mongo db
            options = mongo.db.recovery.find()
            return render_template("new_entry.html", options = options, date_difference=date_difference)

        else:
            flash("You have made today's entry already!")
            return redirect(url_for("profile", username=username))

    # IndexError statement if the user does not have any entries since account creation
    except IndexError as error:
        # if the user posts
        if request.method == "POST":
            # grab the users username
            username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]
            # call the get_result() function
            result = get_result(username)

            # get the choices made by the user on their entry form
            final_attributes = request.form.getlist("options.choice")
            # create the total counter
            total = 0

            # set up the attribute queries to get each individual response
            attr_1_query = final_attributes[0]
            attr_2_query = final_attributes[1]
            attr_3_query = final_attributes[2]
            attr_4_query = final_attributes[3]
            attr_5_query = final_attributes[4]
            attr_6_query = final_attributes[5]
            attr_7_query = final_attributes[6]
            attr_8_query = final_attributes[7]

            # The below if statements match the user's responses on an 
            # attribute-by-attribute basis and get the correct values from the constant dictionaries.
            # The resulting score is then added to the above total counter
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

            # create the dictionary entry for mongo db
            entry = {
                "option_choice": request.form.getlist("options.choice"),
                "created_by": session["user"],
                "user_chosen_date": request.form.get("date_choice"),
                "submission_date": datetime.today().strftime('%Y-%m-%d'),
                "comment_text": request.form.get("comment_text"),
                "name": mongo.db.users.find_one({"username": session["user"]})["_id"],
                "score": total
            }
            # insert the user entry
            mongo.db.entries.insert_one(entry)
            flash("Entry Successfully Added")
            return redirect(url_for("profile", username=username))

        # grab the forms options
        options = mongo.db.recovery.find()
        return render_template("new_entry.html", options = options)

    else:
        abort(500)


# Route for the user to view all entries on the all_entries page
@app.route("/all_entries")
def all_entries():
    # grab the users username
    username = mongo.db.users.find_one({"username": session["user"]})

    # if the user is in session
    if session['user']:
        # get all the entries ever made and turn into a list
        full_entries = mongo.db.entries.find()
        full_entries_list = list(full_entries)

        # https://www.programiz.com/python-programming/methods/list/reverse
        # reverse the list
        reversed_list = full_entries_list.reverse()
        return render_template("all_entries.html", full_entries_list=full_entries_list)
    
    else:
        abort(404)


# Route for the user to search all entries based on username
@app.route("/search_entries", methods=["GET", "POST"])
def search_entries():
    # grab the users username
    username = mongo.db.users.find_one({"username": session["user"]})

    # get the users search input
    query_entry = request.form.get("query_entry")

    # Index creation: https://docs.mongodb.com/manual/indexes/
    # find the users search input in the database
    entries = list(mongo.db.entries.find({"$text": {"$search": query_entry}}))
    
    return render_template("all_entries.html", full_entries_list=entries)


# Route for the administrator to manage users profiles based on username
@app.route("/manage_users/", methods=["GET", "POST"])
def manage_users():
    # grab the username of the user
    username = mongo.db.users.find_one({"username": session["user"]})

    # Only admin can access this page
    if session['user'] == 'admin':
        # get all users and turn into a list
        full_users = mongo.db.users.find()
        full_users_list = list(full_users)
        
        return render_template("manage_users.html", full_users_list=full_users_list)

    else:
        abort(404)


# Route for the administrator to search all users based on username
@app.route("/search_users", methods=["GET", "POST"])
def search_users():
    # grab the username
    username = mongo.db.users.find_one({"username": session["user"]})
    # Only admin can access this page
    if session['user'] == "admin":
        username = mongo.db.users.find_one({"username": session["user"]})

        # get the users search input 
        query_user = request.form.get("query_user")

        # Index creation: https://docs.mongodb.com/manual/indexes/
        # find the users search input in the database
        users = list(mongo.db.users.find({"$text": {"$search": query_user}}))
        
        return render_template("manage_users.html", full_users_list=users)


# Route for the administrator to delete all users based on username
@app.route("/delete_user/<username>", methods=["GET", "POST"])
def delete_user(username):
    # get the username of the user
    username_admin = mongo.db.users.find_one({"username": session["user"]})
    # Only admin can access this page
    if session['user'] == "admin":
        # remove the user
        mongo.db.users.remove({"username": username})
        # remove all entries made by the deleted user
        mongo.db.entries.remove({"created_by": username})

        flash("Removal done")
        return redirect(url_for("about"))

    else:
        abort(404)

# function to get the date of the last entry by the user
def get_date(username):
    # try statement in case the user has not submitted an entry yet
    try:
        # get the username
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        # find the latest entry made by the user
        latest_entry_date = mongo.db.entries.find({"created_by": username}).sort(username, -1)
        
        # iterate through the latest entry and return the final date of the entry
        initial_list_date = list(latest_entry_date)
        last_entry_date = initial_list_date[-1]
        last_entry_list_date = list(last_entry_date.items())
        final_date = last_entry_list_date[3][1]
        return final_date
    
    # IndexError if the user has no previous submissions
    except IndexError as error:
        # use of datetime to get todays date
        todays_date = datetime.today().strftime('%Y-%m-%d')
        return todays_date


# function to get the result of the users recovery score based on the entry form submission
def get_result(username):
    # try statement to see if the user has submitted an entry for today
    try:
        # grab the username
        username = mongo.db.users.find_one(
            {"username": session["user"]})["username"]

        # find the latest entry
        latest_entry = mongo.db.entries.find({"created_by": username}).sort(username, -1)
        
        # get the options chosen by the user on their entry for today
        initial_list = list(latest_entry)
        last_entry = initial_list[-1]
        last_entry_list = list(last_entry.items())
        final_attributes = last_entry_list[1][1]

        # start the total counter
        total = 0

        # The below if statements match the user's responses on an 
        # attribute-by-attribute basis and get the correct values from the constant dictionaries.
        # The resulting score is then added to the above total counter.
        # Note that the score calculation/attribute querying is compliant with the DRY principle.
        # Despite the formulae looking similar for the edit_entry, new_entry & get_result sections of
        # this file, based on varying factors they are pulling different stored dictionary information to get
        # the necessary attributes selected 
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

    # IndexError narrative return for users that havent submitted an entry for today
    except IndexError as error:
        narrative = "No entry yet, please submit one"
        return narrative


# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 500 error handler
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
