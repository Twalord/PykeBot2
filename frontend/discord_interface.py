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
    pb_d_queue: asyncio.PriorityQueue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, command_prefix=prefix)


pb = PykeBot()


async def run_discord_bot_loop(pb_d_queue: asyncio.Queue):
    d_token = load_token("DiscordToken")
    pb.pb_d_queue = pb_d_queue
    await pb.login(d_token)
    await pb.connect()


@pb.event
async def on_ready():
    logger.info(f'Logged in as {pb.user.name}')
    logger.info(f'with id {pb.user.id}')

    await pb.change_presence(activity=Game(name=".pb ping", start=datetime.datetime.now()))


@pb.event
async def on_message(message):
    if message.content.startswith('.pb'):
        if message.content.startswith('.pb ping'):
            await message.channel.send("Pong")
        else:
            await initiate_query(message)


async def initiate_query(message):
    logger.debug(f"Received query: {str(message.content)}")
    query = Query(message.content, "discord", message.channel)
    pb.pb_d_queue.put_nowait(query)

"""
@pb.command(name="ping", pass_context=True)
async def ping(ctx):
    logger.debug("Received ping.")
    await ctx.send("Pong!")


@pb.command(name=" ", pass_context=True)
async def initiate_query(ctx, *args):
    logger.debug("Received query.")
    query = Query(args, "discord", ctx)
    pb.pb_d_queue.put_nowait(query)
"""
