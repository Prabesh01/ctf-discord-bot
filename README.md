### multiple-server-support branch

In this branch,
 - all features from main branch.
 - Multiple server support!
  - Work flow: in webfront, server owners logs with discord and selects one of server he owns. then he is logged in as admin for that server (username = serverid). He can edit password and share with others to let others manage as well. 
 - No scoring system
 - one new table than main branch to hold settings for each servers. .env file was used in main branch
 - things got lil complex. still getting way more output than efforts input. so all good.
 - admin user is just there to view and delete data if required. It cannot add or edit other user's data. Have to go through discord oauth to create a login as a discord server admin.
 - Normal User can however view and edit only their challenges/settings/categories. One user cant see other users data.