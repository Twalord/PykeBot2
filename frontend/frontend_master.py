"""
:author: Jonathan Decker
"""


import asyncio


async def loop_back_dummy(forward_queue: asyncio.Queue, frontend_master_queue: asyncio.Queue):
    """
    :description: A dummy Coroutine that sends incoming queries back to the discord interface.
    :param forward_queue: The forward_queue which should be handled by the query_forwarder.
    :type forward_queue: asyncio.Queue
    :param frontend_master_queue: The Queue that is handled by this Coroutine.
    :type frontend_master_queue: asyncio.Queue
    :return: None
    :rtype: None
    """
    while True:
        query = await frontend_master_queue.get()
        query.forward_to = "discord"
        query.output_message = query.command
        forward_queue.put_nowait(query)
        frontend_master_queue.task_done()
