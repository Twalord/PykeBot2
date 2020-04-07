"""
:author: Jonathan Decker
"""

from dataclasses import dataclass
import logging
from discord import Message
from models.data_models import Payload
from models.lookup_tables import next_step_lookup, forward_to_lookup
from models.errors import InvalidForwardToError, InvalidNextStepError
from typing import Set

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
    data: str
    flags: Set[str]
    payload: Payload
    next_step: str

    def __init__(self, context_type: str, forward_to: str, next_step: str, raw_command: str = "",
                 discord_channel: Message.channel = None, data: str = "", output_message: str = "",
                 flags: Set[str] = None, payload: Payload = None):
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
        if forward_to not in forward_to_lookup:
            logger.error(f"Failed to create query as forward_to could not be matched: {forward_to}")
            raise InvalidForwardToError

        if next_step not in next_step_lookup:
            logger.error(f"Failed to create query as next_step could not be matched: {next_step}")
            raise InvalidNextStepError

        self.raw_command = raw_command
        self.context_type = context_type
        self.discord_channel = discord_channel
        self.output_message = output_message
        self.payload = payload
        self.data = data
        self.flags = flags
        self.forward_to = forward_to
        self.next_step = next_step

    def __str__(self):
        """
        :description:
        :return: Returns the command followed by the context_type fields for now.
        :rtype: str
        """
        return str(f"{self.raw_command}, {self.context_type}")

    def update_query(self, forward_to, next_step, data: str = None, flags: Set[str] = None, output_message: str = None, payload: Payload = None):
        """

        :param forward_to:
        :type forward_to:
        :param next_step:
        :type next_step:
        :param data:
        :type data:
        :param flags:
        :type flags:
        :param output_message:
        :type output_message:
        :param payload:
        :type payload:
        :return:
        :rtype:
        """
        if forward_to not in forward_to_lookup:
            logger.error(f"Failed to create query as forward_to could not be matched: {forward_to}")
            raise InvalidForwardToError

        if next_step not in next_step_lookup:
            logger.error(f"Failed to create query as next_step could not be matched: {next_step}")
            raise InvalidNextStepError

        self.forward_to = forward_to
        self.next_step = next_step
        self.data = data
        if flags is not None:
            if self.flags is not None:
                self.flags.union(flags)
            else:
                self.flags = flags
        if output_message is not None:
            self.output_message = output_message
        if payload is not None:
            self.payload = payload
