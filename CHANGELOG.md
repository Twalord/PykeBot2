# 2.1.1
23.8.2020
- Bugfix in toornament_api.py. It now assumes that the custom filed for the summoner name contains the word summoner instead of always being summoner_name. 

# 2.1.0
3.8.2020
- Added toornament_api stalker, by providing a Toornament api token, the api may be used which is faster compared to the HTML scraper
- When using the Toornament api, "Powered by Toornament" and their url is appended to the output
- Discord Bot now logs the version number of discord.py when starting
- Players are now sorted by summonername in the multilinks
- unranked teams are now sorted by team name
- Added flag "no-api" to force using the HTML scraper even when an api token is available
- Added instructions on the Toornament api token to the README
- Updated the version numbers in the requirements.txt to the newest version.

# 2.0.1
- Added the new PykeBot icon
- Removed the old one 

# 2.0
4.7.2020
- Added version numbering and version command
- Added changelog