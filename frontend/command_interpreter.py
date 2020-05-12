"""
Responsible for understanding the raw command in a given Query and setting next step, flags and data accordingly.

:author: Jonathan Decker
"""
from models.query import Query
import logging
from models.lookup_tables import stalk_command_lookup, all_flags_lookup, help_commands_lookup, help_message,\
    uniliga_seitenwahl_commands_lookup, uniliga_seitenwahl_rules
from models.data_models import Error, Message

logger = logging.getLogger("pb_logger")


def interpret_command(query: Query):
    """
    :description: Interprets the raw command of the Query and sets next step, flags and data accordingly.
    :param query: The handled Query.
    :type query: Query
    :return: None
    :rtype: None
    """

    flags = set()
    url = ""
    # fetch raw command
    raw_commands = query.raw_command.split()

    # to drop the .pb at the beginning
    raw_commands.pop(0)

    if len(raw_commands) == 0:
        error_message = f"Command {str(query)} failed, as no command was provided." \
                        f"\nSee '.pb help' for usage."
        logger.error(error_message)
        create_error(query, error_message)
        return

    base_command = raw_commands[0]

    if base_command in stalk_command_lookup:

        # extract data (e.g. url)
        # error case as stalk command needs data
        if len(raw_commands) == 1:
            error_message = f"Command {str(query)} failed, as no data for stalking was provided.\n" \
                            f"See '.pb help' for usage."
            logger.error(error_message)
            create_error(query, error_message)
            return

        # check for flags
        elif len(raw_commands) > 2:
            url = raw_commands[len(raw_commands)-1]
            # everything that is not the base command or the data in the last position is considered a flag
            flags = {*raw_commands[1:-1]}

            # check for invalid flags
            for flag in flags:
                if flag not in all_flags_lookup:
                    error_message = f"Command {str(query)} failed, as an unknown flag '{flag}' was provided.\n" \
                                    f"See '.pb help' for usage."
                    logger.error(error_message)
                    create_error(query, error_message)
                    return

        else:
            url = raw_commands[1]

        # update query so it can be forwarded to backend
        query.update_query("backend", "stalk", data=url, flags=flags)
        return

    elif base_command in help_commands_lookup:
        help_m = Message(help_message)
        query.update_query("frontend", "format", payload=help_m)
        return

    elif base_command in uniliga_seitenwahl_commands_lookup:
        uniliga_m = Message(uniliga_seitenwahl_rules)
        query.update_query("frontend", "format", payload=uniliga_m)
        return

    else:
        error_message = f"Only basic stalking has been implemented so far, command {str(query)} failed.\n" \
                        f"See '.pb help' for usage."
        logger.error(error_message)
        create_error(query, error_message)
        return


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
