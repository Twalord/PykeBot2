"""
Handles scraping of the toornament page.
:author: Jonathan Decker
"""

import asyncio
import logging
import aiohttp
import bs4
from models.data_models import TeamList, Team, Player
from models.errors import NotFoundResponseError, ServerErrorResponseError

logger = logging.getLogger("pb_logger")


# TODO detect case: summoner names are private
# TODO add URL checker


async def stalk_toornament_tournament(toornament_link: str):
    """
    Stalks all teams signed up for the given toornament and returns a TeamList Object
    :raises ServerErrorResponseError, NotFoundResponseError
    :param toornament_link: url to a tournament on toornament
    :type toornament_link: str
    :return: TeamList, containing the Team obj for each signed up team
    :rtype: TeamList
    """

    # edit the link
    toornament_link_list = toornament_link.split("/")
    toornament_link_list.append("participants")
    edited_toornament_link = "/".join(toornament_link_list)

    participants_links = []
    base_url = "https://www.toornament.com"

    async with aiohttp.ClientSession() as session:
        async with session.get(edited_toornament_link) as response:
            if response.status >= 500:
                logger.error(f"Stalking {edited_toornament_link} resulted in a server error.")
                raise ServerErrorResponseError

            # check if toornament page was valid
            if response.status == 404:
                logger.error(f"No tournament could be found for {edited_toornament_link}.")
                raise NotFoundResponseError

            page = await response.text()

        toornament_soup = bs4.BeautifulSoup(page, features="html.parser")
        team_container = toornament_soup.find_all('div', class_="size-1-of-4")

        # extract toornament name
        tournament_name = toornament_soup.select(
            "#main-container > div.layout-section.header > div > section > div > div.information > div.name > h1")[
            0].text

        # multiple team page test
        count = 1
        multipage_toornament = edited_toornament_link + "?page=1"
        while True:
            count += 1
            multipage_toornament = multipage_toornament[:-1] + str(count)
            async with session.get(multipage_toornament) as response:
                page = await response.text()

            toornament_soup = bs4.BeautifulSoup(page, features="html.parser")
            if len(toornament_soup.find_all('div', class_="size-1-of-4")) > 0:
                team_container.extend(toornament_soup.find_all('div', class_="size-1-of-4"))
            else:
                break

        for team in team_container:
            a = team.find('a', href=True)
            participants_links.append(base_url + a['href'])

        # The following syntax exploits async calls to a list of coroutines
        team_list = await asyncio.gather(*(stalk_toornament_team(link, session) for link in participants_links))

        return TeamList(tournament_name, team_list)


async def stalk_toornament_team(toornament_team_link: str, session: aiohttp.ClientSession = None):
    """
    Stalks all players in the given team and returns a Team Object
    :raises ServerErrorResponseError, NotFoundResponseError
    :param toornament_team_link: Link to a toornament team page
    :type toornament_team_link: str
    :param session: A session that can be reused, if none is given, a new one will be created
    :type session: aiohttp.ClientSession
    :return: team containing all players of the given team
    :rtype: Team
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_toornament_team(toornament_team_link, session)

    edited_url = toornament_team_link + "info"
    async with session.get(edited_url) as response:
        if response.status >= 500:
            logger.error(f"Stalking {edited_url} resulted in a server error.")
            raise ServerErrorResponseError

        # check if toornament page was valid
        if response.status == 404:
            logger.error(f"No team could be found for {edited_url}.")
            raise NotFoundResponseError

        page = await response.text()

    toornament_soup = bs4.BeautifulSoup(page, features="html.parser")

    # extract team name
    team_name = \
        toornament_soup.select("#main-container > div.layout-section.header > div > div.layout-block.header > "
                               "div > div.title > div > span")[0].text
    name_containers = toornament_soup.find_all('div', class_="text secondary small summoner_player_id")

    players = []
    for container in name_containers:
        dirty_string = container.text

        dirty_split = dirty_string.split(":")
        # In case someone decides not to enter an actual summoner name
        if len(dirty_split) == 2:
            name = dirty_split[1]
        else:
            continue
        name = name.replace("\n", "")
        name = name.strip()
        players.append(Player(name))

    return Team(team_name, players)
