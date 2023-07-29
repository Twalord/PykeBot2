"""
Provides data models for Player, Team, Team list and Team list list objects.
Further also Error and Message objects are also defined.
All of them are subclasses of Payload which is used in Query.
Finally also Rank is defined.

All payload subclasses define to str and to discord str functions which are used by the output formatter
Player, Team, Team list and Team list list also define extended to str functions
which display further information on the Players and the Rank if possible.

:author: Jonathan Decker
"""

from dataclasses import dataclass, field
from typing import List
import logging
from PykeBot2.models.lookup_tables import rank_str_to_int_lookup, rank_int_to_str_lookup, lp_ranker_threshold
from PykeBot2.models.errors import PayloadCreationError

logger = logging.getLogger("pb_logger")


@dataclass
class Payload:
    def __init__(self):
        logger.error(
            "Payload creation error, something attempted to directly create a payload object, "
            "only subclasses may be created."
        )
        raise PayloadCreationError

    def __str__(self):
        pass

    def extended_str(self):
        pass

    def discord_str(self):
        pass

    def discord_extended_str(self):
        pass


@dataclass
class Rank:
    """
    Saves a player rank as string and integer
    """

    rank_string = "Unknown"
    rank_int = -1
    lp = -1
    lp_ranker = False

    def __init__(self, rank_string: str = None, rank_int: int = None, lp: int = -1,
                 default_for_master_plus: bool = False):
        if rank_string is not None:
            self.rank_int = rank_str_to_int_lookup.get(rank_string.lower(), -1)
            # this ensures that the rank is always written the same way
            self.rank_string = rank_int_to_str_lookup.get(self.rank_int, "Unknown")
        elif rank_int is not None:
            self.rank_int = rank_int
            self.rank_string = rank_int_to_str_lookup.get(rank_int, "Unknown")

        if lp >= 0:
            self.lp = lp

        if self.rank_int >= lp_ranker_threshold:
            self.lp_ranker = True

        if lp == -1 and self.lp_ranker:
            self.lp = (self.rank_int - lp_ranker_threshold) * 100

        if default_for_master_plus and self.lp_ranker:
            self.rank_string = "Master+"

    def __str__(self):
        if self.lp_ranker:
            return f"{self.rank_string} {self.lp}"
        else:
            return self.rank_string

    def __int__(self) -> int:
        # For master+ players increase the rank value by 1 for every 100 lp
        if self.lp_ranker:
            return lp_ranker_threshold + (self.lp // 100)
        return self.rank_int

    def __radd__(self, other):
        # For summing up ranks during average rank calculation
        return other + int(self)


@dataclass
class Player(Payload):
    """
    Saves information on a single league account
    """

    opgg: str
    summoner_name: str
    rank: Rank = field(default_factory=Rank)

    def __init__(self, sum_name):
        self.summoner_name = sum_name
        base_url = "https://" + "euw" + ".op.gg/summoner/userName="
        self.opgg = base_url + self.summoner_name.replace(" ", "")
        rank = Rank()

    def __str__(self):
        if self.rank.rank_int == -1:
            return self.summoner_name
        else:
            return f"{self.summoner_name} {str(self.rank)}"

    def discord_str(self):
        if self.rank.rank_int == -1:
            return self.summoner_name
        else:
            # adds some * for formatting in discord
            return f"{self.summoner_name} *{str(self.rank)}*"

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.summoner_name == other.summoner_name
        return False

    def __lt__(self, other):
        return isinstance(other, Player) and self.summoner_name < other.summoner_name

    def __hash__(self):
        return hash(self.summoner_name)


@dataclass
class Team(Payload):
    """
    Saves information for a team of league players
    """

    name: str
    players: List[Player]
    multi_link: str
    average_rank: Rank = None
    top5_average_rank = None
    max_rank: Rank = None

    def __init__(self, name, players):
        self.name = name
        self.players = list(set(players))
        self.multi_link = self.build_op_gg_multi_link()

    def build_op_gg_multi_link(self):
        """
        construct a valid op.gg multi link for the given summoner names
        :return: String, url to the multilink for the given names
        """
        base_url = f"https://euw.op.gg/multi/query="
        multi_link = base_url
        self.players.sort()
        for player in self.players:
            multi_link += player.summoner_name.replace(" ", "")
            multi_link += "%2C"
        return multi_link

    def __str__(self):
        if self.average_rank is None:
            return f"{self.name} | {self.multi_link}\n"
        else:
            return f"{self.name} t5Ø: {str(self.top5_average_rank)} Ø: {str(self.average_rank)}" \
                   f" max: {str(self.max_rank)} | {self.multi_link}\n"

    def extended_str(self):
        out = str(self)
        sorted_players = sorted(self.players, key=lambda pl: pl.summoner_name)
        for player in sorted_players:
            out += str(player) + " | "
        return out[:-3] + "\n"

    def discord_str(self):
        # adds __ for discord formatting
        if self.average_rank is None:
            return f"__{self.name}__ | {self.multi_link}\n"
        else:
            return f"__{self.name}__ t5Ø: *{str(self.top5_average_rank)}* Ø: *{str(self.average_rank)}*" \
                   f" max: *{str(self.max_rank)}* | {self.multi_link}\n"

    def discord_extended_str(self):
        # needs to call discord_str for each player
        out = self.discord_str()
        sorted_players = sorted(self.players, key=lambda pl: pl.summoner_name)
        for player in sorted_players:
            out += player.discord_str() + " | "
        return out[:-3] + "\n"


@dataclass
class TeamList(Payload):
    """
    Saves a list of teams and the name of the list
    """

    name: str
    teams: List[Team]

    def __init__(self, name, teams):
        self.name = name
        self.teams = teams

    def __str__(self):
        out = f"{self.name}\n\n"
        for team in self.teams:
            out += str(team) + "\n\n"
        out += "\n"
        return out

    def extended_str(self):
        out = f"{self.name} \n\n"
        ranked_teams = [team for team in self.teams if team.average_rank is not None]
        unranked_teams = [team for team in self.teams if team.average_rank is None]
        sorted_ranked_teams = sorted(
            ranked_teams, key=lambda t: t.top5_average_rank.rank_int, reverse=True
        )
        sorted_unranked_teams = sorted(unranked_teams, key=lambda t: t.name)
        for team in sorted_ranked_teams:
            out += team.extended_str() + "\n"
        for team in sorted_unranked_teams:
            out += team.extended_str() + "\n"
        out += "\n"
        return out

    def discord_str(self):
        out = f"__**{self.name}**__ \n"
        for team in self.teams:
            out += team.discord_str() + "\n"
        return out

    def discord_extended_str(self):
        out = f"__**{self.name}**__ \n"
        ranked_teams = [team for team in self.teams if team.average_rank is not None]
        unranked_teams = [team for team in self.teams if team.average_rank is None]
        sorted_teams = sorted(
            ranked_teams, key=lambda t: t.top5_average_rank.rank_int, reverse=True
        )
        for team in sorted_teams:
            out += team.discord_extended_str() + "\n"
        for team in unranked_teams:
            out += team.discord_str() + "\n"
        out += "\n"
        return out


@dataclass
class TeamListList(Payload):
    """
    Saves a list of TeamList objects
    """

    team_lists: List[TeamList]

    def __init__(self, team_lists):
        self.team_lists = team_lists

    def __str__(self):
        out = ""
        for team_list in self.team_lists:
            out += str(team_list)
        return out

    def extended_str(self):
        out = ""
        for team_list in self.team_lists:
            out += team_list.extended_str()
        return out

    def discord_str(self):
        out = ""
        for team_list in self.team_lists:
            out += team_list.discord_str()
        return out

    def discord_extended_str(self):
        out = ""
        for team_list in self.team_lists:
            out += team_list.discord_extended_str()
        return out


@dataclass
class Message(Payload):
    content: str

    def __str__(self):
        out = self.content
        out += "\n"
        return out

    def discord_str(self):
        return str(self)


@dataclass
class Error(Payload):
    content: str

    def __str__(self):
        out = "Error!\n"
        out += self.content
        out += "\n"
        return out

    def discord_str(self):
        out = "__**Error!**__\n"
        out += self.content
        out += "\n"
        return out
