import asyncio
from logging import getLogger
from frontend import discord_interface
from typing import Dict

logger = getLogger('pb_logger')


async def sample_worker(num):
    while True:
        await asyncio.sleep(1)
        logger.debug(f"Sample worker {num} done")


async def dump_que(queue: asyncio.Queue):
    while True:
        query = await queue.get()
        logger.debug(str(query))
        queue.task_done()


async def query_forwarder(forward_queue: asyncio.Queue, sub_module_queues: {str: asyncio.Queue}):
    while True:
        query = await forward_queue.get()
        target_queue = sub_module_queues.get(query.forward_to)
        target_queue.put(query)
        forward_queue.task_done()


def run_main_loop():
    """
    :description: test
    :return:
    :rtype:
    """
    loop = asyncio.get_event_loop()
    try:
        # asyncio.ensure_future(sample_worker(1))
        # asyncio.ensure_future(sample_worker(2))

        # create forward Queue
        forward_queue = asyncio.Queue()

        # create internal Queues
        discord_out_queue = asyncio.Queue()

        # register internal queues
        sub_module_queues = {"discord": discord_out_queue}

        # start query forwarder
        asyncio.ensure_future(query_forwarder(forward_queue, discord_out_queue))

        # start sub modules, each sub module requires its input queue and the forward queue
        asyncio.ensure_future(discord_interface.run_discord_bot_loop(forward_queue))
        asyncio.ensure_future(dump_que(forward_queue))

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
