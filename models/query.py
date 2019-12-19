from dataclasses import dataclass
import logging
from discord import Message

logger = logging.getLogger('pb_logger')


@dataclass
class Query:
    """
    :description:
    """
    command: str
    context_type: str
    discord_channel: Message.channel

    def __init__(self, command, context_type, discord_channel=None):
        self.command = command
        self.context_type = context_type
        self.discord_channel = discord_channel

    def __str__(self):
        return str(f"{self.command}, {self.context_type}")
