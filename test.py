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