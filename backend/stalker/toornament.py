"""
Handles scraping of the toornament page.
:author: Jonathan Decker
"""

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
    :param toornament_link: String, url to a tournament on toornament
    :return: TeamList, containing the Team obj for each signed up team
    """

    # edit the link
    toornament_link_list = toornament_link.split("/")[:-1]
    toornament_link_list.append("participants")
    edited_toornament_link = "/".join(toornament_link_list)

    participants_links = []
    base_url = "https://www.toornament.com"

    async with aiohttp.ClientSession() as session:
        async with session.get(edited_toornament_link) as response:
            if response.status >= 500:
                raise ServerErrorResponseError

            # check if toornament page was valid
            if response.status == 404:
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

        team_list = []
        for link in participants_links:
            team_list.append(await stalk_toornament_team(link, session))

        return TeamList(tournament_name, team_list)


async def stalk_toornament_team(toornament_team_link: str, session: aiohttp.ClientSession = None):
    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_toornament_team(toornament_team_link, session)
    else:
        edited_url = toornament_team_link + "info"
        async with session.get(edited_url) as response:
            if response.status >= 500:
                raise ServerErrorResponseError
            # check if toornament page was valid
            if response.status == 404:
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
            dirt, name = dirty_string.split(":")
            name = name.replace("\n", "")
            name = name.strip()
            players.append(Player(name))

        return Team(team_name, players)
