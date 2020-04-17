"""
Test Prime League stalker and op gg stalker functions.

:author: Jonathan Decker
"""

import sys

import pytest
import os

recreate_test_data = False


@pytest.mark.asyncio
async def test_positive_stalk_prime_league_season():
    from backend.stalker import prime_league
    from models.data_models import TeamListList, TeamList, Team, Player
    from backend.stalker.op_gg_rank import add_team_list_list_ranks

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

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_season"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_season"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result

    # Also test with stalked ranks as well to avoid full stalking primeleague.gg twice

    await add_team_list_list_ranks(team_list_list)

    extended_result_str = team_list_list.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_season_with_ranks"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_season_with_ranks"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result


@pytest.mark.asyncio
async def test_positive_stalk_prime_league_group():
    from backend.stalker import prime_league
    from backend.stalker.op_gg_rank import add_team_list_ranks

    url = "https://www.primeleague.gg/de/leagues/prm/1457-spring-split-2020/group/509-gruppenphase/5498-division-2-1"

    team_list = await prime_league.stalk_prime_league_group(url)

    extended_result_str = team_list.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_group"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_group"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result

    # Also test with stalked ranks as well to avoid full stalking primeleague.gg twice

    await add_team_list_ranks(team_list)

    extended_result_str = team_list.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_group_with_ranks"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_group_with_ranks"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result


@pytest.mark.asyncio
async def test_positive_stalk_prime_league_team():
    from backend.stalker import prime_league
    from backend.stalker.op_gg_rank import add_team_ranks

    url = "https://www.primeleague.gg/de/leagues/teams/90248-esug-ultimate-five-feeders"

    team = await prime_league.stalk_prime_league_team(url)

    extended_result_str = team.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_team"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_team"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result

    # Also test with stalked ranks as well to avoid full stalking primeleague.gg twice

    await add_team_ranks(team)

    extended_result_str = team.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_team_with_ranks"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_prime_league_team_with_ranks"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result
