import sys

import pytest
import os


@pytest.mark.asyncio
async def test_stalk_toornament_team():
    from backend.stalker import toornament
    from models.data_models import TeamList
    url = "https://www.toornament.com/tournaments/2324026559405285376/information"

    team_list = await toornament.stalk_toornament_tournament(url)

    assert len(team_list.teams) > 0
    assert isinstance(team_list, TeamList)

    extended_result_str = team_list.extended_str()

    # Reads expected results from file, beware encodings
    # best to let a successful test write the expected results
    with open(os.path.join(sys.path[0], "expected_result_stalk_toornament"), "r", encoding='utf-8') as file:
        expected_result = file.read()
        assert extended_result_str == expected_result
