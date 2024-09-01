### Action Taken
- bot.py: flag case insensitive check.
- bot.py: fetch_challenges_file: clear challenges before adding new ones
- bot.py: ditch get_close_matches. use starts with. lower()
- remove 10 limit on api/views.py

- .gitignore: uploads/
- remove fields and footer from solve msg embed. content pani!! ping vairaxa
- remove background url from env. add author and category field.
- signals.py: on challenge delete, trigger bot update and remove files 
- pre_save. if over=False: if msg_id edit else add and update add_data. 
- readme images partial

### Remain
- readme images
- notify.py: attacthment/image send to embed

### Later
- Score:
    - models.py: score (Challenge/User).
    - api/bot.py: leaderboard fetch. 
    - api: reset. Clear Solves Table. Lock Challenges. reset solve count to zero. Reset User Scores.
- notify.py: gen_image
- multiple attachments/links
- challenges under game. game start/end time. env=individual game's settings.
- create/join team. team_mandatory
- multiple server?
