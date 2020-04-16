import sys

import pytest
import os

recreate_test_data = True


@pytest.mark.asyncio
async def test_positive_stalk_toornament_tournament():
    from backend.stalker import toornament
    from models.data_models import TeamList

    url = "https://www.toornament.com/tournaments/2324026559405285376/information"

    team_list = await toornament.stalk_toornament_tournament(url)

    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)

    extended_result_str = team_list.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_toornament_tournament"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_toornament_tournament"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result


@pytest.mark.asyncio
async def test_positive_stalk_toornament_team():
    from backend.stalker import toornament
    from models.data_models import Team

    url = "https://www.toornament.com/en_US/tournaments/2324026559405285376/participants/2430790421496733696/"

    team = await toornament.stalk_toornament_team(url)

    assert len(team.players) > 0
    assert isinstance(team, Team)

    extended_result_str = team.extended_str()

    # In case the formatting changes, the test data needs to be recreated and checked manually
    if recreate_test_data:
        with open(os.path.join(sys.path[0], "expected_result_stalk_toornament_team"), "w+", encoding='utf-8') as file:
            file.write(extended_result_str)

    with open(os.path.join(sys.path[0], "expected_result_stalk_toornament_team"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result


@pytest.mark.asyncio
async def test_broken_toornament_link_stalk_toornament_tournament():
    from backend.stalker import toornament
    from models.errors import NotFoundResponseError

    broken_url = "https://www.toornament.com/tournaments/2324076559805285376/information"

    with pytest.raises(NotFoundResponseError):
        team_list = await toornament.stalk_toornament_tournament(broken_url)


@pytest.mark.asyncio
async def test_broken_toornament_team_link_stalk_toornament_team():
    from backend.stalker import toornament
    from models.errors import NotFoundResponseError

    broken_url = "https://www.toornament.com/en_US/tournaments/2324026559405285376/participants/2430790231446233696/"

    with pytest.raises(NotFoundResponseError):
        team = await toornament.stalk_toornament_team(broken_url)


@pytest.mark.asyncio
async def test_broken_link_stalk_toornament_tournament():
    from backend.stalker import toornament
    from aiohttp import ClientConnectorError

    unreachable_url = "https://www.com/"

    with pytest.raises(ClientConnectorError):
        team_list = await toornament.stalk_toornament_tournament(unreachable_url)


@pytest.mark.asyncio
async def test_broken_link_stalk_toornament_team():
    from backend.stalker import toornament
    from aiohttp import ClientConnectorError

    unreachable_url = "https://www.com/"

    with pytest.raises(ClientConnectorError):
        team_list = await toornament.stalk_toornament_team(unreachable_url)
