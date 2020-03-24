from models.query import Query
from dataclasses import dataclass
from models.errors import MainCommandTypeError, SubCommandTypeError
import logging


logger = logging.getLogger("pb_logger")

db_query_types = ["Team", "Player", "Tournament", "Date", "Time_Frame"]
new_info_types = ["Tournament_Link", "Alias"]
refresh_types = ["Team", "Player", "Tournament", "Tournament_Link"]
settings_types = ["Update", "Check"]
other_types = ["Other"]


command_types = {"db_query": db_query_types,
                 "new_info": new_info_types,
                 "refresh": refresh_types,
                 "settings": settings_types,
                 "other": other_types}


@dataclass
class CommandType:

    main_type: str
    sub_type: str

    def __init__(self, main_type: str, sub_type: str):
        if main_type not in command_types.keys():
            raise MainCommandTypeError
        if sub_type not in command_types.get(main_type):
            raise SubCommandTypeError

        self.main_type = main_type
        self.sub_type = sub_type


def interpret_command(query: Query):
    pass
