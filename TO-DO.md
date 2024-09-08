### Changelog

- can't add/edit challenge if invalid webhook url given
- allow users to delete User. Settings permission wont hinder now.

### TO-Do

- flag encryption
- db/models.py solve: unique together(user, challenge)

### Later

- Score:
    - models.py: score (Challenge/User).
    - api/bot.py: leaderboard fetch. 
    - api: reset. Clear Solves Table. Lock Challenges. reset solve count to zero. Reset User Scores.
- notify.py: gen_image
- multiple attachments/links
- create/join team. team_mandatory

### might

 - hint drop
 - add writeup
