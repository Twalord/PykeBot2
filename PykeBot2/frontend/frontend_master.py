"""
Main Frontend module, responsible for calling command interpreter on new queries,
calling output formatter and checking the context before sending a query to the respective interface.

:author: Jonathan Decker
"""


import asyncio
import logging
from PykeBot2.models.lookup_tables import next_step_lookup
from PykeBot2.models.errors import InvalidNextStepError
from PykeBot2.frontend.command_interpreter import interpret_command
from PykeBot2.frontend.output_formatter import format_payload

logger = logging.getLogger("pb_logger")


async def loop_back_dummy(forward_queue: asyncio.Queue, frontend_queue: asyncio.Queue):
    """
    :description: A dummy Coroutine that sends incoming queries back to the discord interface.
    :param forward_queue: The forward_queue which should be handled by the query_forwarder.
    :type forward_queue: asyncio.Queue
    :param frontend_queue: The Queue that is handled by this Coroutine.
    :type frontend_queue: asyncio.Queue
    :return: None
    :rtype: None
    """
    while True:
        query = await frontend_queue.get()
        query.forward_to = "discord"
        query.output_message = query.command
        forward_queue.put_nowait(query)
        frontend_queue.task_done()


async def frontend_loop(forward_queue: asyncio.Queue, frontend_queue: asyncio.Queue):
    """
    :description: Main Coroutine for the frontend. Responsible for calling command interpreter and output formatter.
    :param forward_queue: The Queue which is handled by the forwarder of the main event loop.
    :type forward_queue: asyncio.Queue
    :param frontend_queue: The Queue that is handled by this Coroutine.
    :type frontend_queue: asyncio.Queue
    :return: None
    :rtype: None
    """

    while True:
        query = await frontend_queue.get()
        try:
            if query.next_step not in next_step_lookup:
                raise InvalidNextStepError
        except InvalidNextStepError:
            logger.error(f"Invalid next_step in query {str(query)}, discarding query.")
            del query
            frontend_queue.task_done()
            continue

        # could use a dict here, instead of multiple elif checks but with only 3 there is not much point
        if query.next_step == "interpret":
            # call command interpreter with query
            interpret_command(query)
            # send query to forward_queue
            forward_queue.put_nowait(query)

        elif query.next_step == "format":
            # call output formatter with query
            format_payload(query)
            # send query to forward_queue (should be self submit)
            forward_queue.put_nowait(query)

        elif query.next_step == "display":
            # check query context type, set forward_to and send to forward_queue
            if query.context_type == "discord":
                query.forward_to = "discord"
                forward_queue.put_nowait(query)

            else:
                logger.error(
                    f"Invalid context_type in query {str(query)}, discarding query."
                )
                del query
                frontend_queue.task_done()
                continue

        else:
            # Next_step can't be handled by frontend, something went wrong
            logger.error(
                f"Invalid control flow in frontend master for query {str(query)}, discarding query."
            )
            del query

        frontend_queue.task_done()
