from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger('pb_logger')


@dataclass
class Rank:
    """
    Saves a player rank as string and integer
    """
    string = ""
    rating = -1

    def __init__(self, rank_string, rating):
        self.string = rank_string
        self.rating = rating

    def __str__(self):
        return self.string


@dataclass
class Player:
    """
    Saves information on a single league account
    """
    opgg: str
    summoner_name: str
    rank: Rank = Rank("", -1)

    def __init__(self, sum_name):
        self.summoner_name = sum_name
        base_url = "https://" + "euw" + ".op.gg/summoner/userName="
        self.opgg = base_url + self.summoner_name.replace(" ", "")

    def __str__(self):
        if Rank.rating == -1:
            return self.summoner_name
        else:
            return f"{self.summoner_name} {str(self.rank)}"


@dataclass
class Team:
    """
    Saves information for a team of league players
    """
    name: str
    players: List[Player]
    multi_link: str
    average_rank: Rank = None
    max_rank: Rank = None

    def __init__(self, name, players):
        self.name = name
        self.players = players
        self.multi_link = self.build_op_gg_multi_link()

    def build_op_gg_multi_link(self):
        """
        construct a valid op.gg multi link for the given summoner names
        :return: String, url to the multilink for the given names
        """
        base_url = f"https://euw.op.gg/multi/query="
        multi_link = base_url
        for player in self.players:
            multi_link += player.summoner_name.replace(" ", "")
            multi_link += "%2C"
        return multi_link

    def __str__(self):
        if self.average_rank is None:
            return f"{self.name} | {self.multi_link}"
        else:
            return f"{self.name} Ø: {str(self.average_rank)} max: {str(self.max_rank)} | {self.multi_link}"

    def extended_str(self):
        out = str(self) + "\n"
        sorted_teams = sorted(self.players,
                              key=lambda player: player.summoner_name)
        for player in sorted_teams:
            out += str(player) + " | "
        return out[:-3]


@dataclass
class TeamList:
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
        return out

    def extended_str(self):
        out = f"{self.name} \n"
        # sorted_teams = sorted(self.teams, key=lambda team: lookup_tables.rank_lookup.get(str(team.average_rank).lower()), reverse=True)
        # for team in sorted_teams:
        for team in self.teams:
            out += team.extended_str() + "\n"
        return out


@dataclass
class TeamListList:
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
