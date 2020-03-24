"""
:author: Jonathan Decker
"""

from dataclasses import dataclass
import logging
from discord import Message
from frontend.command_interpreter import CommandType

logger = logging.getLogger('pb_logger')


@dataclass
class Query:
    """
    :description: Class for any type of data that is sent around via Queues.
    Should mainly be created by ingoing interfaces.
    While processing the query the fields should be further filled out and updated.
    """
    raw_command: str
    context_type: str
    discord_channel: Message.channel
    forward_to: str
    output_message: str
    # TODO add Payload to transport data from backend to frontend

    def __init__(self, raw_command: str, context_type: str, discord_channel: Message.channel = None,
                 forward_to: str = "frontend", output_message: str = "", command: CommandType = None):
        """
        :description: For new Query Objects its assumed they originate from some interface
         and should be forwarded to the frontend.
        :param raw_command: The actual command issued by the user.
        :type raw_command: str
        :param context_type: The type of context the command was issued or should go back to e.g. discord, cli
        :type context_type: str
        :param discord_channel: In case the command comes from a discord chat interface,
         the channel needs to be saved in order to answer in the same channel.
        :type discord_channel: Message.channel
        :param forward_to: The next sub module that needs to handle the query. Used by the query forwarder.
        :type forward_to: str
        :param output_message: The message that should be sent back to the user via the channel.
        :type output_message: str
        """
        self.raw_command = raw_command
        self.context_type = context_type
        self.discord_channel = discord_channel
        self.forward_to = forward_to
        self.output_message = output_message

    def __str__(self):
        """
        :description:
        :return: Returns the command followed by the context_type fields for now.
        :rtype: str
        """
        return str(f"{self.raw_command}, {self.context_type}")
