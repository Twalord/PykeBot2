"""
Uses undocumented Battlefy API to scrape tournament participants.

:author: Jonathan Decker
"""

import logging
import aiohttp
from PykeBot2.models.data_models import TeamList, Team, Player
import bs4
import json

# from backend.stalker.op_gg_rank import calc_average_and_max_team_rank

logger = logging.getLogger("pb_logger")


async def stalk_battlefy_tournament(battlefy_url: str):
    """
    Uses undocumented Battlefy API to scrape tournament participants.
    :param battlefy_url: A valid url to a battlefy tournament.
    :type battlefy_url: str
    :return: a TeamList object containing all Teams and Players of the given tournament.
    :rtype: TeamList
    """

    # extract tournament id from url
    battlefy_url_split = battlefy_url.split("/")

    tournament_id = battlefy_url_split[5]

    # create link for http request by inserting the tournament id
    tournament_api_url = (
        f"https://dtmwra1jsgyb0.cloudfront.net/tournaments/{tournament_id}/teams?"
    )

    # make the request
    async with aiohttp.ClientSession() as session:
        async with session.get(tournament_api_url) as response:
            page = await response.text()

    # parse the data to create Team and Player Objects
    soup = bs4.BeautifulSoup(page, features="html.parser")

    json_data = json.loads(soup.text)

    # print(json.dumps(json_data, indent=4, separators=(". ", " = ")))

    teams = []

    for team in json_data:
        team_name = team["name"]
        players = []
        for player in team["players"]:
            player_name = player["inGameName"]
            player_obj = Player(player_name)
            # ranks are often not up to date so just normal rank addition for now
            # try to add rank if player stats are available
            # player_stats = player.get("stats", None)
            # if player_stats is not None:
            #    player_rank_str = player_stats["tier"] + " " + player_stats["rank"]
            #    player_rank = Rank(rank_string=player_rank_str)
            #    player_obj.rank = player_rank
            players.append(player_obj)
        new_team = Team(team_name, players)
        # calc_average_and_max_team_rank(new_team)
        teams.append(new_team)

    team_list = TeamList(battlefy_url_split[4], teams)

    return team_list
