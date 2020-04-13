"""
Test Summoners inn cup stalker.

:author: Jonathan Decker
"""

import sys

import pytest
import os

recreate_test_data = True


@pytest.mark.asyncio
async def test_positive_stalk_summoners_inn_cup():
    from backend.stalker import summoners_inn

    url = "https://www.summoners-inn.de/de/leagues/hausarrest/1468-cup-1/participants"

    team_list = await summoners_inn.stalk_summoners_inn_cup(url)

    extended_result_str = team_list.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_cup"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_cup"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result


@pytest.mark.asyncio
async def test_positive_stalk_summoners_inn_team():
    from backend.stalker import prime_league, summoners_inn

    url = "https://www.summoners-inn.de/de/leagues/hausarrest/1468-cup-1/teams/90176-team-fail-flash"

    team = await prime_league.stalk_prime_league_team(url)

    extended_result_str = team.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_team"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_team"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result
