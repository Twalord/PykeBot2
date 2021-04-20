"""
:author: Jonathan Decker
"""


import asyncio
from logging import getLogger
from PykeBot2.frontend import discord_interface, frontend_master
from PykeBot2.backend import backend_master
from PykeBot2.models.lookup_tables import forward_to_lookup

logger = getLogger("pb_logger")


async def sample_worker(num: int):
    """
    :description: Example for coroutine functionality, does not do any meaningful work.
    :param num: Number only used to track the worker in logs.
    :type num: int
    :return: None
    :rtype: None
    """
    while True:
        await asyncio.sleep(1)
        logger.debug(f"Sample worker {num} done")


async def dump_que(queue: asyncio.Queue):
    """
    :description: Coroutine to dump the contents of a Queue into the log and clear the Queue. Only used for debugging.
    :param queue: The queue to dump.
    :type queue: asyncio.Queue
    :return: None
    :rtype: None
    """
    while True:
        query = await queue.get()
        logger.debug(str(query))
        queue.task_done()


async def query_forwarder(
    forward_queue: asyncio.Queue, sub_module_queues: {str: asyncio.Queue}
):
    """
    :description: Coroutine that manages the forward_queue and reads the forward_to field of incoming queries.
    Based on the value of the field the query is submitted to the next Queue.
    :param forward_queue: The forward_queue that is awaited by this Coroutine.
    :type forward_queue: asyncio.Queue
    :param sub_module_queues: A dictionary that maps the short names of each sub module to its Queue.
    :type sub_module_queues: {str: asyncio.Queue}
    :return: None
    :rtype: None
    """
    while True:
        query = await forward_queue.get()
        forward_to = query.forward_to
        if forward_to not in forward_to_lookup:
            logger.error(f"Invalid forward_to in query {str(query)}, discarding query.")
            del query
            continue
        target_queue = sub_module_queues.get(forward_to)
        target_queue.put_nowait(query)
        forward_queue.task_done()


def run_main_loop():
    """
    :description: The main loop of the program. Uses asyncio event loop and ensures all main Coroutines.
    Further all Queue objects are created here as they need to be present when starting the Coroutines.
    :return: None
    :rtype: None
    """
    loop = asyncio.get_event_loop()
    try:
        # create forward Queue
        forward_queue = asyncio.Queue()

        # create internal Queues
        discord_out_queue = asyncio.Queue()
        frontend_master_queue = asyncio.Queue()
        backend_master_queue = asyncio.Queue()

        # register internal queues
        sub_module_queues = {
            "discord": discord_out_queue,
            "frontend": frontend_master_queue,
            "backend": backend_master_queue,
        }

        # start query forwarder
        asyncio.ensure_future(query_forwarder(forward_queue, sub_module_queues))

        # start sub modules, each sub module requires its input queue and the forward queue
        asyncio.ensure_future(
            discord_interface.run_discord_bot_loop(forward_queue, discord_out_queue)
        )
        asyncio.ensure_future(
            frontend_master.frontend_loop(forward_queue, frontend_master_queue)
        )
        asyncio.ensure_future(
            backend_master.backend_loop(forward_queue, backend_master_queue)
        )

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
