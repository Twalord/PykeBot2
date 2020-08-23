"""
Handles scraping of the toornament page using the official toornament API.

:author: Jonathan Decker
"""

import requests
import logging
import aiohttp
import bs4
from typing import List

from models.data_models import TeamList, Team, Player
from utils import token_loader
from models.errors import NotFoundResponseError, ServerErrorResponseError


logger = logging.getLogger("pb_logger")


async def stalk_toornament_api_tournament(toornament_link: str) -> TeamList:
    """
    Stalks teams in the given toornament link using the toornament api.
    A valid token in a file called ToornamentToken must be in the working directory for this.
    :param toornament_link: A valid link to a toornament tournament
    :type toornament_link: str
    :return: A TeamList object containing all teams from the given tournament
    :rtype: TeamList
    """
    api_token = token_loader.load_token("ToornamentToken")

    tournament_id = toornament_link.split("/")[5]
    participant_resource_url = f"https://api.toornament.com/viewer/v2/tournaments/{tournament_id}/participants"

    edited_toornament_link = "/".join(toornament_link.split("/")[:6])

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

        # extract toornament name
        tournament_name = toornament_soup.select(
            "#main-container > div.layout-section.header > div > section > div > div.information > div.name > h1")[
            0].text

        participants = []
        i = 0
        while True:
            range_from = i * 50
            range_to = i * 50 + 49
            i += 1

            headers = {"X-Api-Key": api_token,
                       "Range": f"participants={range_from}-{range_to}"}

            async with session.get(participant_resource_url, headers=headers) as response:

                if response.status == 206 or response.status == 200:
                    response_json = await response.json()
                    participants.extend(response_json)
                else:
                    break

    return parse_participants(participants, tournament_name)


def parse_participants(participants: List[dict], tournament_name: str) -> TeamList:
    """
    Parses the given participant list and tournament name to create a TeamList object.
    :param participants: Expects a participant list created from the toornament api.
    :type participants: list[dict]
    :param tournament_name: The name of the tournament.
    :type tournament_name: str
    :return: A TeamList object created from the given participant list and tournament name.
    :rtype: TeamList
    """
    total = {}
    for team in participants:
        total[team["id"]] = team

    teams = []
    for team_entry in total.values():
        team_name = team_entry["name"]
        team_lineup = team_entry["lineup"]
        players = []
        for lineup_entry in team_lineup:
            custom_fields = lineup_entry["custom_fields"]
            keys = custom_fields.keys()
            summoner_name_field = None
            for key in keys:
                if "summoner" in key:
                    summoner_name_field = key
                    break
            if summoner_name_field is None:
                continue
            player_summoner_name = lineup_entry["custom_fields"][summoner_name_field]

            if player_summoner_name is None:
                continue
            player = Player(player_summoner_name)
            players.append(player)
        team = Team(team_name, players)
        teams.append(team)

    team_list = TeamList(tournament_name, teams)
    return team_list


def fetch_participants(toornament_link: str, api_token:str) -> List[dict]:
    tournament_id = toornament_link.split("/")[5]

    participant_resource_url = f"https://api.toornament.com/viewer/v2/tournaments/{tournament_id}/participants"

    participants = []

    i = 0
    while True:
        range_from = i*50
        range_to = i*50 + 49
        i += 1

        headers = {"X-Api-Key": api_token,
                   "Range": f"participants={range_from}-{range_to}"}

        r = requests.get(participant_resource_url, headers=headers)

        # print(r.status_code)
        if r.status_code == 206 or r.status_code == 200:
            # print(r.json())
            participants.extend(r.json())
        else:
            break

    return participants


def fetch_stages(toornament_link: str, api_token: str):
    tournament_id = toornament_link.split("/")[5]
    headers = {"X-Api-Key": api_token}

    stages_resource_url = f"https://api.toornament.com/viewer/v2/tournaments/{tournament_id}/stages"

    r = requests.get(stages_resource_url, headers=headers)

    print(r)
    # print(r.json())
    for ele in r.json():
        print(ele)
        print("\n")


def fetch_matches(toornament_link: str, api_token: str):
    tournament_id = toornament_link.split("/")[5]
    matches_resource_url = f"https://api.toornament.com/viewer/v2/tournaments/{tournament_id}/matches"

    i = 0
    while True:
        range_from = i*128
        range_to = i*128 + 127
        i += 1
        headers = {"X-Api-Key": api_token,
                   "Range": f"matches={range_from}-{range_to}"}

        r = requests.get(matches_resource_url, headers=headers)

        print(r.status_code)
        if r.status_code == 206 or r.status_code == 200:
            print(r.json())
        else:
            break


def fetch_groups(toornament_link: str, api_token: str):
    tournament_id = toornament_link.split("/")[5]
    group_resource_url = f"https://api.toornament.com/viewer/v2/tournaments/{tournament_id}/groups"

    groups = []
    i = 0
    while True:
        range_from = i*50
        range_to = i*50 + 49
        i += 1
        headers = {"X-Api-Key": api_token,
                   "Range": f"groups={range_from}-{range_to}"}

        r = requests.get(group_resource_url, headers=headers)

        # print(r.status_code)
        if r.status_code == 206 or r.status_code == 200:
            # print(r.json())
            groups.extend(r.json())
        else:
            break

    for ele in groups:
        print(ele)


def fetch_tournament(toornament_link: str) -> str:
    edited_link = "/".join(toornament_link.split("/")[:6])

    r = requests.get(edited_link)

    page = r.text

    toornament_soup = bs4.BeautifulSoup(page, features="html.parser")

    # extract toornament name
    tournament_name = toornament_soup.select(
        "#main-container > div.layout-section.header > div > section > div > div.information > div.name > h1")[
        0].text

    return tournament_name
