ad = mongo.db.entries.find_one( {"$query":{ObjectId(username)}, "$orderby":{"$natural":-1}} )
    print(ad)