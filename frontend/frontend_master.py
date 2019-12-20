import asyncio


async def loop_back_dummy(forward_queue: asyncio.Queue, frontend_master_queue: asyncio.Queue):
    while True:
        query = await frontend_master_queue.get()
        query.forward_to = "discord"
        query.output_message = query.command
        forward_queue.put_nowait(query)
        frontend_master_queue.task_done()
