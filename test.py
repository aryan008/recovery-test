user = mongo.db.users.find_one({"username": session["user"]})
    # Only admin can access this page
    if session['user'] == 'admin':
        print(session['user'])
        full_entries = mongo.db.entries.find()
        full_entries_list = list(full_entries)
        adzy=[]
        for entry in full_entries_list:
            for key in entry:
                print(key)
                if key=="user_chosen_date" or key=="created_by":
                    adzy.append(entry[key])

        print(adzy)