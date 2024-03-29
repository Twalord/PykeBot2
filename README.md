# PykeBot2
[![Documentation Status](https://readthedocs.org/projects/pykebot2/badge/?version=latest)](https://pykebot2.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://github.com/Twalord/PykeBot2/blob/master/LICENSE)

![alt text](./PykeIcon2Resize.png)

PykeBot2 is a Discord Bot for gathering information on League of Legends players participating in tournaments.
Given a link to online tournament, where the summoner names of the players are visible,
PykeBot2 will return op.gg multi-links for each team and optionally the rankings of each player.
Output can be as file or as Discord chat messages.

Supported tournament platforms are:
- [Prime League](https://www.primeleague.gg/de/start)
- [Toornmanet](https://www.toornament.com/en_US/)
- [Summoners Inn](https://www.summoners-inn.de/de/start)
- [Battlefy](https://battlefy.com/)

## But why?
The first version of [PykeBot](https://github.com/Twalord/PykeBot) arose out of an annoyance.
When playing on one of the tournament platforms we would like to have a op.gg multi-link of our opponents to prepare our draft.
So someone has to copy and paste every single player summoner name from the tournament page into the op.gg form.
The first PykeBot was created to automate this process and did so quite well but wasn't designed to be easily expended or easy to use by anyone but its creator.

PykeBot2 was completely redesigned and it is faster and more reliable than the original PykeBot.
It is also probably kinda over-engineered given its simple task.

## Installation
PykeBot2 requires Python Version 3.7+.
The required packages can be installed via `pip install -r requirements.txt`.
Further PykeBot2 requires a Firefox installation on the system and the respective geckodriver for the system.
The download for geckodriver can be found [here](https://github.com/mozilla/geckodriver/releases),
simply place the executable in the same folder as the main.py.
PykeBot2 further requires a valid Discord API token. How to acquire a token is explained [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).
Copy the token to a file called `DiscordToken`. 
The file must contain nothing else but the token and have no file ending.
Start PykeBot2 via `python main.py` in a terminal.

### Optional: Toornament API token
#### Support for Toornament API has ended
Due to changes in the Toornament API and deprecation of the endpoints required for PykeBot2 to use it,
the support for the official Toornament API has ended. 

### Optional: Riot API production key
PykeBot2 supports using the Riot API for Rank stalking instead of the stand HTML op.gg stalker.
For this a valid Riot API production key is required.
The API production key must be placed in a filed called file called 'RiotToken' in the project root, similar to the Discord token.

## How to use
PykeBot2 can be added to one or multiple Discord server, but it also accepts direct messages.
PykeBot2 ignores all messages that do not start with `.pb`.

`.pb help` returns a usage explanation.

`.pb stalk [file] [rank] <url>` starts a stalk for the given `<url>`. 
`file` and `rank` can be given as additional flags.

When `file` is added, the output will be returned as a text file.
When `rank` is added, PykeBot2 will go over every player it found in the tournament and try to add ranks using op.gg.
Adding ranks may take some time as the bot has to go over not only every team but every single player.
For a full Prime League stalk this may take between 20 and 30 minutes.

## Running PykeBot2 as a container
Create the files `DiscordToken`, `RiotToken` and `ToornamentToken` in the base directory of the project and
insert the respective API keys. 
Using Docker run `docker build -t pykebot2:latest .` to build the image and run it with
`docker run --rm pykebot2`.

## How it works
PykeBot2 uses Python asyncio to handle user commands asynchronously. 
This keeps the Discord interface responsive while stalks are performed concurrently.
Incoming commands are handled as query objects which are forwarded between the different parts of the bot.

The stalkers, which perform the actual gathering of the player information, use html requests via aiohttp whenever possible
and selenium when necessary. Starting a headless firefox instance is a lot more expensive in terms of performance
compared to simply making a few html requests. 
As is the way with web scraper like this, the stalker might easily break if a tournament platform changes their website.
As far as I know none of the tournament platforms overs an API for collecting teams and player so all information is collected from html requests.

## Building the docs
The docs are build using sphinx autodoc. Install `sphinx` using pip.
Navigate to the `docs/` folder and run `make html` to rebuild the docs.

To add new files to the documentation run in the root folder of the project `sphinx-apidoc -o "docs/source" "./PykeBot2"`

## Credits
The PykeBot Icon was designed by the talented [Binidi](https://www.deviantart.com/binidi/art/Pyke-Icon-808245658).

## License
This software is made available under the Mozilla Public License Version 2.0.