Out of nowhere i got this idea. Django gives full featured admin panel. 
So I could manage entire discord ctf competitions by only 
- writing django models. (easy admin panel dashboard to create/record challenges)
- trigger some discord webhook functions on db change (easy solves/new challenge notification)
- simple discord.py bot to get flags from users with a slash command (easy flag submission)

 And yes, it took me just one day to build the entire thing. Most part was easy. One place i stuck for quite a while. challenge_pre_save of db/signals.py. Tried everything but couldn't figure what was wrong. It just wasn't working as intended. The lesson learned was:
 - Don't perform actions directly in the pre_save signal; instead, set flags and handle actions in the post_save signal after the object is saved and its state is consistent.
 