"""
Responsible for creating the output message from the payload by calling str messages, respecting flags.

:author: Jonathan Decker
"""

import logging
from models.query import Query
from models.data_models import Error, Payload, Message, TeamList, Team
from models.lookup_tables import as_file_flag_lookup, with_ranks_flag_lookup

logger = logging.getLogger("pb_logger")


def format_payload(query: Query):
    """
    :description: Takes the Payload from the Query and calls to str based on context and flags and saves it to output message.
    :param query: The handled Query.
    :type query: Query
    :return: None
    :rtype: None
    """

    # check for payload
    if not isinstance(query.payload, Payload):
        error_message = f"Command {str(query)} failed, formatter needs a valid payload."
        logger.error(error_message)
        return

    # identify payload and handle error and message case
    if isinstance(query.payload, Error):
        format_error(query)
        return

    if isinstance(query.payload, Message):
        format_message(query)
        return

    # additional case for valid TeamList payloads with 0 teams
    if isinstance(query.payload, TeamList):
        if len(query.payload.teams) == 0:
            error_message = f"Command {str(query)} returned no teams.\n" \
                            f"Are there even valid teams in the given tournament?"
            logger.error(error_message)
            create_error(query, error_message)
            return

    # additional case for valid Team payloads with 0 players
    if isinstance(query.payload, Team):
        if len(query.payload.players) == 0:
            error_message = f"Command {str(query)} returned no players.\n" \
                            f"Are there even valid players in the given team?"
            logger.error(error_message)
            create_error(query, error_message)

    # identify flags,
    rank = False
    file = False

    if len(with_ranks_flag_lookup.intersection(query.flags)) >= 1:
        rank = True

    if len(as_file_flag_lookup.intersection(query.flags)) >= 1:
        file = True

    # identify target display
    # file output should ignore extra formatting for discord
    output = ""
    if query.context_type == "discord" and not file:
        # do discord formatting
        if rank:
            # do extended discord formatting
            output = query.payload.discord_extended_str()
        else:
            # do normal discord formatting
            output = query.payload.discord_str()
    else:
        if rank:
            # do extended formatting
            output = query.payload.extended_str()
        else:
            # do normal formatting
            output = str(query.payload)

    query.update_query("frontend", "display", output_message=output)


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


def format_error(query: Query):
    """
    :description: Formats error payloads, and sets output message.
    :param query: The handled Query.
    :type query: Query
    :return: None
    :rtype: None
    """

    # rank and file flags are ignored as this is an error message
    if query.context_type == "discord":
        query.output_message = query.payload.discord_str()
    else:
        query.output_message = str(query.payload)
    query.next_step = "display"


def format_message(query: Query):
    """
    :description: Formats message payloads, and sets output message.
    :param query: The handled Query.
    :type query: Query
    :return: None
    :rtype: None
    """
    # context is ignored for formatting
    # rank and file flags are also ignored as this is a simple message
    query.output_message = str(query.payload)
    query.next_step = "display"
