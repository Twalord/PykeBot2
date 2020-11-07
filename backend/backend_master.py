"""
Main Backend Module, responsible for calling stalker functions for query data or calling the database interface.
When finished sets the payload field of the query with data object.

:author: Jonathan Decker
"""

import logging
import asyncio
from models.data_models import Error, Message, Payload, Team, TeamListList, TeamList
from models.query import Query
from models.errors import TokenLoadingError
from utils import token_loader
from backend.stalker import op_gg_rank, prime_league, toornament, summoners_inn, battlefy, toornament_api, riot_api_rank
from models.lookup_tables import prime_league_base_url, prime_league_group_key_words, prime_league_season_key_words, \
    prime_league_team_key_words, toornament_base_url, toornament_tournament_key_words, with_ranks_flag_lookup, \
    summoners_inn_base_url, summoners_inn_cup_key_words, summoners_inn_team_key_words, battlefy_base_url, \
    prime_league_use_group_flag_lookup, dont_use_api_flag_lookup, used_toornament_api_flag_lookup,\
    used_riot_api_flag_lookup

logger = logging.getLogger('pb_logger')

"""
Helper dictionaries used to map identifier in the url to stalker functions.
"""
website_type_to_prime_league_stalker = {"group": prime_league.stalk_prime_league_group,
                                        "team": prime_league.stalk_prime_league_team,
                                        "season": prime_league.stalk_prime_league_season}

website_type_to_toornament_stalker = {"tournament": toornament.stalk_toornament_tournament,
                                      "tournament_api": toornament_api.stalk_toornament_api_tournament}

website_type_to_summoners_inn_stalker = {"cup": summoners_inn.stalk_summoners_inn_cup,
                                         "team": prime_league.stalk_prime_league_team}

website_type_to_battlefy_stalker = {"tournament": battlefy.stalk_battlefy_tournament}


async def backend_loop(forward_queue: asyncio.Queue, backend_queue: asyncio.Queue):
    """
    :description: Main Coroutine for the backend. Responsible for calling stalker functions.
    :param forward_queue: The Queue which is handled by the forwarder of the main event loop.
    :type forward_queue: asyncio.Queue
    :param backend_queue: The Queue that is handled by this Coroutine.
    :type backend_queue: asyncio.Queue
    :return: None
    :rtype: None
    """
    while True:
        query = await backend_queue.get()

        # check next_step to perform
        if query.next_step == "stalk":
            stalker = determine_stalker(query)
            logger.debug(f"Using stalker function {stalker.__name__}")

            if stalker is None:
                # if stalker is none an error has occurred during stalker determination and saved to query
                forward_queue.put_nowait(query)
                backend_queue.task_done()
                continue

            # check flags
            ranks = False
            if len(with_ranks_flag_lookup.intersection(query.flags)) >= 1:
                ranks = True

            # extra case for prime league season with ranks
            # in this case a message should inform the user that this might take a moment
            if stalker is prime_league.stalk_prime_league_season and ranks:
                extra_message = Message("Running prime league season stalk with ranks might take a while, also output "
                                        "only as file.")
                extra_query = Query(query.context_type, "frontend", "format", discord_channel=query.discord_channel,
                                    payload=extra_message)
                forward_queue.put_nowait(extra_query)
                query.update_query(query.forward_to, query.next_step, flags="file")

            logger.debug(f"Starting stalk for query: {query.raw_command}")
            try:
                payload = await stalker(query.data)
            # TODO add better error handling based on exception raised
            except Exception as e:
                error_message = f"While stalking a {type(e)} occurred. Original query: {query}"
                logger.exception(error_message)
                create_error(query, error_message)
                forward_queue.put_nowait(query)
                backend_queue.task_done()
                continue
            logger.debug(f"Finished stalking for query: {query.raw_command}")

            # rank stalking is the slowest part and for mid to large sized tournaments it takes some time
            if isinstance(payload, TeamList):
                if len(payload.teams) > 30 and ranks:
                    extra_message = Message(f"Rank stalk for {len(payload.teams)} teams might take a moment, please "
                                            f"wait.")
                    extra_query = Query(query.context_type, "frontend", "format", discord_channel=query.discord_channel,
                                        payload=extra_message)
                    forward_queue.put_nowait(extra_query)

            if ranks:
                logger.debug(f"Starting rank stalk for query: {query.raw_command}")
                # try loading a Riot Api Token
                found_riot_token = False
                try:
                    token_loader.load_token("RiotToken")
                    found_riot_token = True
                except TokenLoadingError as e:
                    logger.info("Failed to load RiotToken, using op.gg instead.")
                if found_riot_token and len(query.flags.intersection(dont_use_api_flag_lookup)) == 0:
                    await call_rank_stalker(payload, use_api=True)
                    query.flags.add(*used_riot_api_flag_lookup)
                else:
                    await call_rank_stalker(payload)
                logger.debug(f"Finished rank stalk for query: {query.raw_command}")

            # adds data to db
            # TODO don't forget to add data

            query.update_query("frontend", "format", payload=payload)

            # forward query
            forward_queue.put_nowait(query)

        # new backend tasks should be added here
        else:
            logger.error(f"Invalid control flow in backend master for query {str(query)}, discarding query.")
            del query

        backend_queue.task_done()


def create_error(query: Query, content: str):
    """
    :description: Creates an error message from the content and adds it to the query,
    further sets query forward to to frontend and next step to format.
    :param query: The handled query, which encountered an error.
    :type query: Query
    :param content: The error message to be displayed, should usually include str(query).
    :type content: str
    :return: None
    :rtype: None
    """
    error = Error(content)
    query.update_query("frontend", "format", payload=error)


def determine_stalker(query: Query):
    """
    :description: Checks the url for keywords to determine the correct stalker.
    :param query: The handled Query.
    :type query: Query
    :return: The stalker function fitting the url.
    :rtype: function (coroutine)
    """
    prime_league_str = "prime_league"
    toornament_str = "toornament"
    summoners_inn_str = "summoners_inn"
    battlefy_str = "battlefy"
    url = query.data
    website = None
    website_type = None

    if prime_league_base_url in url:
        website = prime_league_str
    elif toornament_base_url in url:
        website = toornament_str
    elif summoners_inn_base_url in url:
        website = summoners_inn_str
    elif battlefy_base_url in url:
        website = battlefy_str
    else:
        error_message = f"Invalid url for query {str(query)}, url {url} could not be matched with a stalker."
        logger.error(error_message)
        create_error(query, error_message)
        return None

    if website == prime_league_str:
        # Force group stalking in case the season stalk is not possible yet
        if len(prime_league_use_group_flag_lookup.intersection(query.flags)) >= 1:
            website_type = "group"
            # fix url in this case
            url = query.data
            url_split = url.split("/")[:7]
            url_split.append("participants")
            url = "/".join(url_split)
            query.data = url

        elif all(elem in url.split("/") for elem in prime_league_group_key_words):
            website_type = "group"
        elif all(elem in url.split("/") for elem in prime_league_team_key_words):
            website_type = "team"
        # check season last as its keywords are a subset of the other sets
        elif all(elem in url.split("/") for elem in prime_league_season_key_words):
            website_type = "season"
        else:
            error_message = f"Invalid url for query {str(query)}, url {url} was matched with prime league but no " \
                            f"season, group or team were found. "
            logger.error(error_message)
            create_error(query, error_message)
            return None

        return website_type_to_prime_league_stalker.get(website_type)

    if website == toornament_str:
        if all(elem in url.split("/") for elem in toornament_tournament_key_words):
            website_type = "tournament"

            # fix url in case the url is not the base url for the tournament by cutting unneeded extension
            query.data = "/".join(query.data.split("/")[:6])

        else:
            error_message = f"Invalid url for query {str(query)}, url {url} was matched with toornament but no " \
                            f"tournament was found. "
            logger.error(error_message)
            create_error(query, error_message)
            return None

        found_toornament_api_token = False
        # try loading a Toornament Api Token
        try:
            token_loader.load_token("ToornamentToken")
            found_toornament_api_token = True
        except TokenLoadingError as e:
            logger.info("Failed to load ToornamentToken, using HTML scraper.")

        if found_toornament_api_token and not len(dont_use_api_flag_lookup.intersection(query.flags)) >= 1:
            website_type = website_type + "_api"
            query.flags.add(*used_toornament_api_flag_lookup)
        return website_type_to_toornament_stalker.get(website_type)

    if website == summoners_inn_str:
        if all(elem in url.split("/") for elem in summoners_inn_team_key_words):
            website_type = "team"
        elif all(elem in url.split("/") for elem in summoners_inn_cup_key_words):
            website_type = "cup"
        else:
            error_message = f"Invalid url for query {str(query)}, url {url} was matched with summoners-inn but no " \
                            f"tournament was found. "
            logger.error(error_message)
            create_error(query, error_message)
            return None

        return website_type_to_summoners_inn_stalker.get(website_type)

    if website == battlefy_str:
        # only tournament is supported and the url gives no further clues
        website_type = "tournament"

        return website_type_to_battlefy_stalker.get(website_type)


async def call_rank_stalker(payload: Payload, use_api=False):
    """
    :description: Checks the payload type and calls the correct rank stalker.
    :param payload: The Payload object returned from stalking. Submitting Error, Message or Player will cause an error.
    :type payload: Payload
    :param use_api: If set to true, will try to use the Riot api to fetch ranks instead of op.gg.
    :type use_api: Bool
    :return: None
    :rtype: None
    """
    # determine what the payload is to call the respective op gg rank function

    if use_api:
        api_token = token_loader.load_token("RiotToken")
    if isinstance(payload, TeamListList):
        if use_api:
            await riot_api_rank.add_team_list_list_ranks(payload, api_token)
        else:
            await op_gg_rank.add_team_list_list_ranks(payload)
    elif isinstance(payload, TeamList):
        if use_api:
            await riot_api_rank.add_team_list_ranks(payload, api_token)
        else:
            await op_gg_rank.add_team_list_ranks(payload)
    elif isinstance(payload, Team):
        if use_api:
            await riot_api_rank.add_team_ranks(payload, api_token)
        else:
            await op_gg_rank.add_team_ranks(payload)
    else:
        logger.error(
            f"Failed to identify payload for rank addition, payload is for some reason of type {type(payload)}")
