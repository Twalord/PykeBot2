"""
Uses the riot api to fetch the ranks of players

:author: Jonathan Decker
"""

import asyncio
import logging
import ssl

import aiohttp
import time
import json
import certifi
from PykeBot2.models.data_models import Player, Rank, Team, TeamList, TeamListList

logger = logging.getLogger("pb_logger")


async def stalk_player_riot_api(sum_name: str, api_token: str, session=None) -> (str, int):
    """
    Uses the riot api to find the soloQ ranking of the given player.
    :param sum_name: Summoner name of the player.
    :type sum_name: str
    :param api_token: Valid Riot api token.
    :type api_token: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession or RateLimiter
    :return: Tuple with string representation of the rank of the player and the current lp or -1 if not found.
    :rtype: (str, int)
    """

    if session is None:
        async with aiohttp.ClientSession() as session:
            session = RateLimiter(session)
            return await stalk_player_riot_api(sum_name, api_token, session)

    summoner_resource_url = (
        f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{sum_name}"
    )

    headers = {"X-Riot-Token": api_token}

    sslcontext = ssl.create_default_context(cafile=certifi.where())

    async with await session.get(summoner_resource_url, headers=headers, ssl=sslcontext) as r:
        r_json = await r.json()

    if r.status == 429:
        logger.debug(
            f"Rate limit exceeded! {session.request_counter} Requests made in {time.monotonic() - session.start_time} seconds."
        )
        await asyncio.sleep(60)
        return await stalk_player_riot_api(sum_name, api_token, session)
    summoner_id = r_json.get("id", "None")
    if summoner_id == "None":
        return "", -1

    league_resource_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"

    async with await session.get(league_resource_url, headers=headers, ssl=sslcontext) as r:
        r_data = await r.read()
    try:
        r_json = json.loads(r_data)
    except json.JSONDecodeError:
        logger.error(f"Decoding failed for {r_data}")
        return "", -1

    if r.status == 429:
        logger.debug(
            f"Rate limit exceeded! {session.request_counter} Requests made in {time.monotonic() - session.start_time} seconds."
        )
        await asyncio.sleep(60)
        return await stalk_player_riot_api(sum_name, api_token, session)

    if type(r_json) is dict:
        r_json = [r_json]
    elif type(r_json) is None:
        return "", -1
    tier = ""
    rank = ""
    lp = -1
    for league in r_json:
        queue_type = league.get("queueType", "None")
        if queue_type == "RANKED_SOLO_5x5":
            tier = league["tier"]
            rank = league["rank"]
            lp = league["leaguePoints"]
            break
    if tier == "":
        # logger.debug(f"{sum_name} has no rank. {r_json}")
        return "", -1
    return f"{tier} {rank}", lp


async def add_player_rank(player: Player, api_token: str, session=None):
    """
    :description: Calls stalk player riot using the summoner name of the given Player and adds a Rank obj to the Player.
    :param player: A Player obj with a summoner name.
    :type player: Player
    :param api_token: Valid Riot api token.
    :type api_token: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession  or RateLimiter
    :return: None
    :rtype: None
    """
    if session is None:
        async with aiohttp.ClientSession() as session:
            session = RateLimiter(session)
            return await add_player_rank(player, api_token, session)

    rank_string, lp = await stalk_player_riot_api(player.summoner_name, api_token, session)
    player.rank = Rank(rank_string=rank_string, lp=lp)
    return


async def add_team_ranks(team: Team, api_token: str, session=None):
    """
    :description: Calls add player rank for each player of the given team. Also sets the average and max team rank.
    :param team: A team with a list of players.
    :type team: Team
    :param api_token: Valid Riot api token.
    :type api_token: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession or RateLimiter
    :return: None
    :rtype: None
    """
    if session is None:
        async with aiohttp.ClientSession() as session:
            session = RateLimiter(session)
            return await add_team_ranks(team, api_token, session)

    await asyncio.gather(
        *(add_player_rank(player, api_token, session) for player in team.players)
    )

    calc_average_and_max_team_rank(team)
    return


async def add_team_list_ranks(team_list: TeamList, api_token: str, session=None):
    """
    :description: Calls add team ranks for each team in the given team list obj.
    :param team_list: A team list with a list of teams.
    :type team_list: TeamList
    :param api_token: Valid Riot api token.
    :type api_token: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession or RateLimiter
    :return: None
    :rtype: None
    """
    if session is None:
        async with aiohttp.ClientSession() as session:
            session = RateLimiter(session)
            return await add_team_list_ranks(team_list, api_token, session)

    # calling gather here causes instability. Due to too many calls?
    for team in team_list.teams:
        await add_team_ranks(team, api_token, session)
    # await asyncio.gather(*(add_team_ranks(team, session) for team in team_list.teams))
    return


async def add_team_list_list_ranks(
    team_list_list: TeamListList, api_token: str, session=None
):
    """
    :description: Calls add team list ranks for each team list in the given team list list obj.
    :param team_list_list: A team list list with a list of team lists.
    :type team_list_list: TeamListList
    :param api_token: Valid Riot api token.
    :type api_token: str
    :param session: When a session already exits, it should be reused as much as possible for better performance.
    :type session: aiohttp.ClientSession or RateLimiter
    :return: None
    :rtype: None
    """
    if session is None:
        # custom connector to limit parallel connection pool, to avoid crashes
        conn = aiohttp.TCPConnector(limit=20)
        async with aiohttp.ClientSession(connector=conn) as session:
            session = RateLimiter(session)
            return await add_team_list_list_ranks(team_list_list, api_token, session)

    # calling gather here causes instability. Due to too many calls?
    for team_list in team_list_list.team_lists:
        await add_team_list_ranks(team_list, api_token, session)
    # await asyncio.gather(*(add_team_list_ranks(team_list, session) for team_list in team_list_list.team_lists))

    return


def calc_average_and_max_team_rank(team: Team):
    """
    :description: Calculates the average and maximum rank of a given team.
    If a player is unranked or the rank is unknown, then the player is ignored for the average.
    :param team: A team obj with players who have Rank objs.
    :type team: Team
    :return: None
    :rtype: None
    """
    ranks = []
    for player in team.players:
        if player.rank is not None and player.rank.rank_int > 0:
            ranks.append(player.rank)

    if len(ranks) == 0:
        average = 0
        max_rank = Rank(rank_int=0)
        top5_average_rank = 0
    else:
        average = round(sum(ranks) / len(ranks))
        #max_rank = max(int(rank) for rank in ranks)
        max_rank = max(team.players, key=lambda p: p.rank.rank_int + (p.rank.lp / 100)).rank

        if len(ranks) < 5:
            top5_average_rank = average
        else:
            ranks.sort(key=lambda r: int(r), reverse=True)
            top5_average_rank = round(sum(ranks[:5])/5)

    team.average_rank = Rank(rank_int=average, default_for_master_plus=True)
    team.max_rank = Rank(rank_int=max_rank.rank_int, lp=max_rank.lp)
    team.top5_average_rank = Rank(rank_int=top5_average_rank, default_for_master_plus=True)
    return


class RateLimiter:
    # Personal/Test key rate limit
    # rate = 5/6
    # max_tokens = 20.0

    # Production key rate limit
    rate = 50  # should be 50
    max_tokens = 500  # 500
    regen_after = 60.0

    request_counter = 0
    start_time = 0

    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.tokens = self.rate
        self.updated_at = time.monotonic()

    async def get(self, *args, **kwargs):
        await self.wait_for_tokens()
        if self.request_counter == 0:
            self.start_time = time.monotonic()
        self.request_counter += 1
        return self.session.get(*args, **kwargs)

    async def wait_for_tokens(self):
        while self.tokens <= 1.0:
            self.add_new_tokens()
            # should be shorter and use exponential back-off
            await asyncio.sleep(self.regen_after)
        self.tokens -= 1.0

    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        new_tokens = float(time_since_update) * self.rate
        if self.tokens + new_tokens >= 1.0:
            self.tokens = min(self.tokens + new_tokens, self.max_tokens)
            self.updated_at = now


"""    def add_new_tokens(self):
        now = time.monotonic()
        time_since_update = now - self.updated_at
        if time_since_update > self.regen_after:
            self.tokens = self.max_tokens
            self.updated_at = now"""
