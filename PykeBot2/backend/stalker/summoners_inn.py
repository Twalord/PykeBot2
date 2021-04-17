"""
Handles scraping of summoners inn with focus on the hausarrest cup.
:author: Jonathan Decker
"""

import asyncio
import logging
import aiohttp
import bs4
from PykeBot2.backend.stalker.prime_league import stalk_prime_league_team
from PykeBot2.models.data_models import TeamList

logger = logging.getLogger("pb_logger")


async def stalk_summoners_inn_cup(
    summoners_inn_cup_link: str, session: aiohttp.ClientSession = None
):
    """
    Takes a link to a summoners inn cup, extracts all team links and uses the prime league team stalker, to stalk the teams.
    :param summoners_inn_cup_link: A valid link to a summoners inn cup like Hausarrest.
    :type summoners_inn_cup_link: str
    :param session: A reusable ClientSession
    :type session: aiohttp.ClientSession
    :return: A team list containing all teams of the cup.
    :rtype: TeamList
    """
    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_summoners_inn_cup(summoners_inn_cup_link, session)

    # edit url and cut any unneeded extensions
    main_page_url = "/".join(summoners_inn_cup_link.split("/")[:7])

    participants_url = main_page_url + "/participants"

    # get title from main cup page
    async with session.get(main_page_url) as response:
        # TODO add error handling
        page = await response.text()

    soup = bs4.BeautifulSoup(page, features="html.parser")
    title = soup.title.string.split("»")[0].strip()

    # get list of team links
    async with session.get(participants_url) as response:
        # TODO add error handling
        page = await response.text()

    soup = bs4.BeautifulSoup(page, features="html.parser")

    # somehow does not return the correct block, so grab all possible links instead and filter them
    # list_container = soup.find('table', class_="table table-fixed-single table-responsive")

    # extract all teams
    team_links = [link["href"] for link in soup.find_all("a", href=True)]

    team_links = list(dict.fromkeys(team_links))

    # team_links = filter(filter_team_links, team_links)

    # all valid teams have 'teams' in their ulr and are of a certain length
    team_links = [
        link for link in team_links if "teams" in link and len(link.split("/")) >= 9
    ]

    teams = await asyncio.gather(
        *(stalk_prime_league_team(link, session) for link in team_links)
    )

    filter_teams = [team for team in teams if team]

    # filter out teams that have not registered at least 5 players
    filter_teams = [team for team in filter_teams if len(team.players) >= 5]

    return TeamList(title, filter_teams)


def filter_team_links(link):
    """
    Helper function to filter out non team links.
    :param link: Str, a web link
    :return: Bool, true if the link contains a teams, false if not
    """
    link_split = link.split("/")
    for split in link_split:
        if split == "teams":
            return True
    return False
