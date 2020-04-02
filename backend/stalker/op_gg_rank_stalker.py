"""
Uses op.gg for player rank stalking and offers further functions
for adding ranks to teams and calculating average rankings.

:author: Jonathan Decker
"""

import asyncio
import logging
import bs4
import aiohttp
from models.data_models import Player, Rank, Team, TeamList, TeamListList

logger = logging.getLogger("pb_logger")


async def stalk_player_op_gg(sum_name: str, session: aiohttp.ClientSession = None):

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await stalk_player_op_gg(sum_name, session)

    # For now lookups are region locked for euw
    base_url = "https://euw.op.gg/summoner/userName="
    url = base_url + sum_name.replace(" ", "+")

    async with session.get(url) as response:
        page = await response.text()

    soup = bs4.BeautifulSoup(page, features="html.parser")

    # to remove leading and trailing /n and /t
    elo = soup.find('div', class_="TierRank")
    if elo is not None:
        return ' '.join(elo.text.split()).lower()
    else:
        return "Unknown"


async def add_player_rank(player: Player, session: aiohttp.ClientSession = None):

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await add_player_rank(player, session)

    player.rank = Rank(rank_string=await stalk_player_op_gg(player.summoner_name, session))
    return


async def add_team_ranks(team: Team, session: aiohttp.ClientSession = None):

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await add_team_ranks(team, session)

    await asyncio.gather(*(add_player_rank(player, session) for player in team.players))

    calc_average_and_max_team_rank(team)
    return


async def add_team_list_ranks(team_list: TeamList, session: aiohttp.ClientSession = None):

    if session is None:
        async with aiohttp.ClientSession() as session:
            return await add_team_list_ranks(team_list, session)

    # calling gather here causes instability. Due to too many calls?
    for team in team_list.teams:
        await add_team_ranks(team, session)
    # await asyncio.gather(*(add_team_ranks(team, session) for team in team_list.teams))
    return


async def add_team_list_list_ranks(team_list_list: TeamListList, session: aiohttp.ClientSession = None):

    if session is None:
        # custom connector to limit parallel connection pool, to avoid crashes
        conn = aiohttp.TCPConnector(limit=20)
        async with aiohttp.ClientSession(connector=conn) as session:
            return await add_team_list_list_ranks(team_list_list, session)

    # calling gather here causes instability. Due to too many calls?
    for team_list in team_list_list.team_lists:
        await add_team_list_ranks(team_list, session)
    # await asyncio.gather(*(add_team_list_ranks(team_list, session) for team_list in team_list_list.team_lists))

    return


def calc_average_and_max_team_rank(team: Team):

    ranks = []
    for player in team.players:
        if player.rank is not None and player.rank.rank_int > 0:
            ranks.append(player.rank)

    if len(ranks) == 0:
        average = 0
        max_rank = 0
    else:
        average = round(sum(ranks) / len(ranks))
        max_rank = max(rank.rank_int for rank in ranks)

    team.average_rank = Rank(rank_int=average)
    team.max_rank = Rank(rank_int=max_rank)
    return
