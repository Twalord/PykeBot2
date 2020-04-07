"""

:author: Jonathan Decker
"""

import logging
import asyncio
from models.data_models import Error, Message, Payload, Team, TeamListList, TeamList
from models.query import Query
from backend.stalker import op_gg_rank, prime_league, toornament
from models.lookup_tables import prime_league_base_url, prime_league_group_key_words, prime_league_season_key_words, \
    prime_league_team_key_words, toornament_base_url, toornament_tournament_key_words, with_ranks_flag_lookup

logger = logging.getLogger('pb_logger')

website_type_to_prime_league_stalker = {"group": prime_league.stalk_prime_league_group,
                                        "team": prime_league.stalk_prime_league_team,
                                        "season": prime_league.stalk_prime_league_season}

website_type_to_toornament_stalker = {"tournament": toornament.stalk_toornament_tournament}


async def backend_loop(forward_queue: asyncio.Queue, backend_queue: asyncio.Queue):
    while True:
        query = await backend_queue.get()

        # check next_step to perform
        if query.next_step == "stalk":
            stalker = determine_stalker(query)

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
                logger.error(error_message)
                create_error(query, error_message)
                forward_queue.put_nowait(query)
                backend_queue.task_done()
                continue
            logger.debug(f"Finished stalking for query: {query.raw_command}")

            if ranks:
                logger.debug(f"Starting rank stalk for query: {query.raw_command}")
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
    error = Error(content)
    query.update_query("frontend", "format", payload=error)


def determine_stalker(query: Query):
    prime_league_str = "prime_league"
    toornament_str = "toornament"
    url = query.data
    website = None
    website_type = None

    if prime_league_base_url in url:
        website = prime_league_str
    elif toornament_base_url in url:
        website = toornament_str
    else:
        error_message = f"Invalid url for query {str(query)}, url {url} could not be matched with a stalker."
        logger.error(error_message)
        create_error(query, error_message)
        return None

    if website == prime_league_str:
        if all(elem in url.split("/") for elem in prime_league_group_key_words):
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

        return website_type_to_toornament_stalker.get(website_type)


async def call_rank_stalker(payload: Payload):
    # determine what the payload is to call the respective op gg rank function

    if isinstance(payload, TeamListList):
        await op_gg_rank.add_team_list_list_ranks(payload)
    elif isinstance(payload, TeamList):
        await op_gg_rank.add_team_list_ranks(payload)
    elif isinstance(payload, Team):
        await op_gg_rank.add_team_ranks(payload)
    else:
        logger.error(
            f"Failed to identify payload for rank addition, payload is for some reason of type {type(payload)}")
