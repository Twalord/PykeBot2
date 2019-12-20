import logging
import asyncio
from discord.ext import commands
from discord import Game
import datetime

from utils.token_loader import load_token
from models.query import Query

logger = logging.getLogger('pb_logger')
prefix = ".pb"


class PykeBot(commands.Bot):
    forward_queue: asyncio.Queue
    output_queue: asyncio.Queue

    async def output_queue_listener(self):
        await self.wait_until_ready()
        while not self.is_closed():
            query = await self.output_queue.get()
            await query.discord_channel.send(query.output_message)
            self.output_queue.task_done()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, command_prefix=prefix)
        self.output_queue_listener = self.loop.create_task(self.output_queue_listener())


pb = PykeBot()


async def run_discord_bot_loop(forward_queue: asyncio.Queue, output_queue: asyncio.Queue):
    d_token = load_token("DiscordToken")
    pb.forward_queue = forward_queue
    pb.output_queue = output_queue
    await pb.login(d_token)
    await pb.connect()


@pb.event
async def on_ready():
    logger.info(f'Logged in as {pb.user.name}')
    logger.info(f'with id {pb.user.id}')

    await pb.change_presence(activity=Game(name=".pb ping", start=datetime.datetime.now()))


@pb.event
async def on_message(message):
    if message.content.startswith('.pb') and pb.user.id != message.author.id:
        if message.content.startswith('.pb ping'):
            await message.channel.send("Pong")
        else:
            await initiate_query(message)


async def initiate_query(message):
    logger.debug(f"Received query: {str(message.content)}")
    query = Query(message.content, "discord", message.channel)
    pb.forward_queue.put_nowait(query)
