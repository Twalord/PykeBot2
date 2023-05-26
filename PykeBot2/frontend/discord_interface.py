"""
:author: Jonathan Decker
"""
import io
import logging
import asyncio
from discord.ext import commands
import datetime
from discord import Message, File, Game, __version__, Intents

from PykeBot2.utils.token_loader import load_token
from PykeBot2.models.query import Query
from PykeBot2.models.lookup_tables import as_file_flag_lookup
from PykeBot2.models.data_models import Error

logger = logging.getLogger("pb_logger")
prefix = ".pb"


class PykeBot(commands.Bot):
    """
    :description: Overwrites the standard Discord Bot to add fields for the incoming and outgoing Queues as well as
    background tasks. The prefix for co
    """

    forward_queue: asyncio.Queue
    output_queue: asyncio.Queue

    async def output_queue_listener(self):
        """
        :description: Coroutine that handles the discord output queue and sends messages based on the incoming queries.
        The query objects is not further forwarded.
        :return: None
        :rtype: None
        """
        await self.wait_until_ready()
        while not self.is_closed():
            query = await self.output_queue.get()

            # check if send as file, in case of error always skip file flag
            if len(
                    as_file_flag_lookup.intersection(query.flags)
            ) >= 1 and not isinstance(query.payload, Error):

                # prepare file creation
                title = query.output_message.split("\n", 1)[0]
                mem_file = io.StringIO(query.output_message)

                # create discord file and send it
                out_file = File(mem_file, filename=(title + ".txt"))
                await query.discord_channel.send(
                    f"Finished stalking {title}.", file=out_file
                )

            # else chunk message
            else:
                out_list = chunk_message(query.output_message)
                for out in out_list:
                    await query.discord_channel.send(out)

            self.output_queue.task_done()

    async def setup_hook(self) -> None:
        self.output_queue_listener = self.loop.create_task(self.output_queue_listener())

    def __init__(self, *args, **kwargs):
        """
        :description: Initialises the bot without Queues and sets up the output queue listener.
        Is once called when discord_interface is imported.
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """
        intents = Intents.none()
        intents.messages = True
        intents.message_content = True
        super().__init__(*args, **kwargs, command_prefix=prefix, intents=intents)


pb = PykeBot()


async def run_discord_bot_loop(
        forward_queue: asyncio.Queue, output_queue: asyncio.Queue
):
    """
    :description: Main Coroutine for the Discord Bot interface.
    Handles the final setup steps and starts the main Coroutine for Discord Bot.
    :param forward_queue: Where queries created from incoming messages are put.
    :type forward_queue: asyncio.Queue
    :param output_queue: The message from queries in this Queue will be send back via the interface.
    :type output_queue: asyncio.Queue
    :return: None
    :rtype: None
    """
    d_token = load_token("DiscordToken")
    pb.forward_queue = forward_queue
    pb.output_queue = output_queue
    await pb.login(d_token)
    logger.info(f"Stating Discord Bot, using discord.py version {__version__}")
    await pb.connect()


@pb.event
async def on_ready():
    """
    :description: Event triggered when the Discord Bot is ready. Logs the event and sets the presence for the bot.
    :return: None
    :rtype: None
    """
    logger.info(f"Logged in as {pb.user.name}")
    logger.info(f"with id {pb.user.id}")
    logger.info("PykeBot2 is ready!")

    await pb.change_presence(
        activity=Game(name=".pb help", start=datetime.datetime.now())
    )


@pb.event
async def on_message(message: Message):
    """
    :description: Event triggered when a message is send to a viewed channel.
    If the message starts with the prefix (standard: '.pb'), a query is created from the message and forwarded.
    Another exception is {prefix} ping which results in an immediate Pong instead of a Query.
    :param message: The message object that triggered the event.
    :type message: discord.Message
    :return: None
    :rtype: None
    """
    if message.content.startswith(prefix) and pb.user.id != message.author.id:
        if message.content.startswith(f"{prefix} ping"):
            await message.channel.send("Pong")
        else:
            initiate_query(message)


def initiate_query(message: Message):
    """
    :description: Creates query object from the given message and submits it to the forward query.
    :param message: A valid message, usually captured by the on_message event.
    :type message: discord.Message
    :return: None
    :rtype: None
    """
    logger.debug(f"Received query: {str(message.content)}")
    query = Query(
        "discord",
        "frontend",
        "interpret",
        raw_command=message.content,
        discord_channel=message.channel,
    )
    pb.forward_queue.put_nowait(query)


def chunk_message(out_raw: str):
    chunk_size = 2000
    out_splits = out_raw.split("\n")
    out_list = []
    message = ""
    for split in out_splits:
        if len(message + split) > chunk_size:
            out_list.append(message)
            message = ""
        message += "\n" + split
    out_list.append(message)

    return out_list
