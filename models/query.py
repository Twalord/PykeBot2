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
    forward_to: str
    output_message: str

    def __init__(self, command, context_type, discord_channel=None, forward_to="frontend", output_message=""):
        self.command = command
        self.context_type = context_type
        self.discord_channel = discord_channel
        self.forward_to = forward_to
        self.output_message = output_message

    def __str__(self):
        return str(f"{self.command}, {self.context_type}")
