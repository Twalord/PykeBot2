import sys

import pytest
import os


@pytest.mark.asyncio
async def test_positive_stalk_prime_league_season():
    from backend.stalker import prime_league
    from models.data_models import TeamListList, TeamList, Team, Player

    url = "https://www.primeleague.gg/de/leagues/prm/1457-spring-split-2020"

    team_list_list = await prime_league.stalk_prime_league_season(url)

    assert len(team_list_list.team_lists) > 0
    assert isinstance(team_list_list, TeamListList)
    for team_list in team_list_list.team_lists:
        assert len(team_list.teams) > 0
        assert isinstance(team_list, TeamList)
        for team in team_list.teams:
            assert isinstance(team, Team)
            for player in team.players:
                assert isinstance(player, Player)

    extended_result_str = team_list_list.extended_str()

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_season"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result
