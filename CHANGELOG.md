# 2.2.4
7.11.2020
- Added note about riot api to readme
- Change to how Riot API rate limit is calculated to avoid exceeding the Rate Limit

# 2.2.3
7.11.2020
- Got approval for a production API key
- Changed rate limits in RateLimiter to the ones for the production key
- merged Riot API branch into master

# 2.2.2
4.8.2020
- Added legal boilerplate for riot api

# 2.2.1
4.8.2020
- The Riot Api rate limit is now no longer exceeded, but using the test key is still slower compared to using op.gg

# 2.2.0
4.8.2020
- Added Riot Api for rank stalking as an alternative to the op gg stalker, however the rate limit of the api is quickly exceeded

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