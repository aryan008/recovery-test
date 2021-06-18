from bson.objectid import ObjectId

ad = [{'_id': ObjectId('60ccbee8647e593dd07cb02c'), 'option_choice': ['No', 'Not at all', 'Yes - Tough session(s)', 'Less than 6 hours', 'Exhausted/Tired', '<1 Litre', 'No', 'No'], 'created_by': 'adamryan', 'user_chosen_date': '2021-06-18', 'submission_date': '2021-06-18', 'comment_text': 'dsdas', 'name': ObjectId('60bb733159cbab4d801372fa'), 'score': 32}, {'_id': ObjectId('60ccbf1a7d29baee17a71088'), 'option_choice': ['Yes - Ice Bath/Sea Swim', 'Very nutritious', 'No', '7.5+ hours', 'Good/Fresh', '3+ Litres', 'No', 'No'], 'created_by': 'adamryan', 'user_chosen_date': '2021-06-17', 'submission_date': '2021-06-18', 'comment_text': 'dadda', 'name': ObjectId('60bb733159cbab4d801372fa'), 'score': 86}, {'_id': ObjectId('60ccbf327d29baee17a71089'), 'option_choice': ['Yes - Ice Bath/Sea Swim', 'Very nutritious', 'Yes - Tough session(s)', 'Less than 6 hours', 'Exhausted/Tired', '<1 Litre', 'No', 'No'], 'created_by': 'adamryan', 'user_chosen_date': '2021-06-18', 'submission_date': '2021-06-18', 'comment_text': 'ccd', 'name': ObjectId('60bb733159cbab4d801372fa'), 'score': 42}]

a = dict(ad)

print(a)