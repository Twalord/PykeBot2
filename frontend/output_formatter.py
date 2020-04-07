"""

:author: Jonathan Decker
"""

import logging
from models.query import Query
from models.data_models import Error, Payload, Message
from models.lookup_tables import as_file_flag_lookup, with_ranks_flag_lookup

logger = logging.getLogger("pb_logger")


def format_payload(query: Query):

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

    # identify flags,
    rank = False
    file = False

    if with_ranks_flag_lookup.intersection(query.flags) >= 1:
        rank = True

    if as_file_flag_lookup.intersection(query.flags) >= 1:
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
    error = Error(content)
    query.update_query("frontend", "format", payload=error)


def format_error(query: Query):

    # rank and file flags are ignored as this is an error message
    if query.context_type == "discord":
        query.output_message = query.payload.discord_str()
    else:
        query.output_message = str(query.payload)
    query.next_step = "display"


def format_message(query: Query):

    # context is ignored for formatting
    # rank and file flags are also ignored as this is a simple message
    query.output_message = str(query.payload)
    query.next_step = "display"
