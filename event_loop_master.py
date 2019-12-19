import asyncio
from logging import getLogger

logger = getLogger('pb_logger')


async def sample_worker(num):
    while True:
        await asyncio.sleep(1)
        logger.debug(f"Sample worker {num} done")


def run_main_loop():
    """
    :description: test
    :return:
    :rtype:
    """
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(sample_worker(1))
        asyncio.ensure_future(sample_worker(2))

        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
