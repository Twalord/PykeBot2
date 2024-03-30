# 2.6.4
- Upgraded dependencies versions to patch vulnerabilities

# 2.6.3
- Fix for toornament stalking to work with change in html selector for toornament titles

# 2.6.2
- Fix to calculation of average and max rank for master+ teams

# 2.6.1
- Fixed prime league group stalking

# 2.6.0
- Added support for League Points in Ranks
- Now displays League Points for Master+ players
- Team averages are calculated while considering LP of Master+ players with 100 LP being equal to 1 division

# 2.5.0
- Added Support for Emerald rank
- Bumped dependency versions for discord.py and aiohttp

# 2.4.3
- Added intents setting for discord bot setup
- Fixed SSL error when accessing Riot API
- Made dataclass usage compatible with Python 3.11
- Set Dockerfile to use Python 3.11 and Geckodriver 0.33.0

# 2.4.2
- Cleaned up requirements.txt

# 2.4.1
- Changed dependency from nextcord back to discord.py

# 2.4.0
- Removed unnecessary files from root folder including riot.txt and project.toml
- Recreated docs setup to get autodocs working with sphinx
- Added instructions for building docs to README.md

# 2.3.2
- Toornament API was disabled so the check for the API token has been disabled and the HTML scraper updated

# 2.3.1
- Token loader now removes newlines in tokens which might cause security issues with http headers

# 2.3.0
- Changed dependency from discord.py to nextcord

# 2.2.12
- Added average rank of top 5 players per team
- Teams are now sorted by the top 5 player average rank

# 2.2.11
20.4.2021
- Added main.py in root folder as additional entry point
- Added project.toml to work with Cloud Native Build pack
- PykeBot2 can now be containerized using 
  `pack build PykeBot2 --builder gcr.io/buildpacks/builder:v1 --env GOOGLE_ENTRYPOINT="python3 main.py"`

# 2.2.10
17.04.2021
- Changed Project structure and moved project code to subfolder PykeBot2
- Automatic refactoring

# 2.2.9
19.03.2021
- Change in Toornament api stalker to use player name if summoner name is not found
- Reduced wait time in riot API rank stalker for new tokens to generate

# 2.2.8
13.03.2021
- Changed Riot API rank stalker to retry after a delay, if it failed a request due to hitting the rate limit

# 2.2.7
28.11.2020
- Added error handling to decoding error to fix it really this time

# 2.2.6
28.11.2020
- Fixed decoding error in riot api

# 2.2.5
28.11.2020
- Fixed bug in Riot API RateLimiter
- Adjusted rate limit

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