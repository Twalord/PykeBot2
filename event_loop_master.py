import asyncio
from logging import getLogger
from frontend import discord_interface

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
        pb_d_queue = asyncio.Queue()
        asyncio.ensure_future(discord_interface.run_discord_bot_loop(pb_d_queue))
        asyncio.ensure_future(dump_que(pb_d_queue))

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
