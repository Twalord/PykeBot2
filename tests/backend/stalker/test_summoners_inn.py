"""
Test Summoners inn cup stalker.

:author: Jonathan Decker
"""

import sys

import pytest
import os

recreate_test_data = False


@pytest.mark.asyncio
async def test_positive_stalk_summoners_inn_cup():
    from PykeBot2.backend.stalker import summoners_inn

    url = "https://www.summoners-inn.de/de/leagues/hausarrest/1492-playoffs"

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
    from PykeBot2.backend.stalker import prime_league

    url = "https://www.summoners-inn.de/de/leagues/hausarrest/1492-playoffs/teams/115966-esug-ultimate-five-feeders"

    team = await prime_league.stalk_prime_league_team(url)

    extended_result_str = team.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_team"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_summoners_inn_team"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result
