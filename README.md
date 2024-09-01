Out of nowhere i got this idea. Django gives full featured admin panel. 
So I could manage entire discord ctf competitions by only 
- writing django models. (easy admin panel dashboard to create/record challenges)
- trigger some discord webhook functions on db change (easy solves/new challenge notification)
- simple discord.py bot to get flags from users with a slash command (easy flag submission)

As i started, to keep this simple, I used some not-so-professional workaround for Bot-Django Communication:
 - Bot needs to fetch challenge title, id and flag from django. Everytime any of these are changes or new challenge is added, django creates a file and saves the json data on it. Bot checks this file every minute. Id file exists, it loads the challenges and deletes the file. Till django creates it again once new change occurs in db.
 - As challenges are dynamic, during flag submission to bot by users, it isn't possible to provide slash command choices. User have to type challenge title or latest added challenge is pressumed by default. Using difflib's get_close_matches to compare user provided challenge name and available challenge names.
 - Bot compares give flag and replies if it is correct. Then Bot submits flags through an django's csrf_extempt endpoint /api/submit_flag. Now django records the solve into the database. With the trigger (post_save receiver) set, webhook notification about the solve will be annouced if it passses the criteria mentioned in .env file.

 And yes, it took me just one day to build the entire thing. Most part was easy. One place i stuck for quite a while. challenge_pre_save of db/signals.py. Tried everything but couldn't figure what was wrong. It just wasn't working as intended. The lesson learned was:
 - Don't perform actions directly in the pre_save signal; instead, set flags and handle actions in the post_save signal after the object is saved and its state is consistent.
