import pytest


@pytest.mark.asyncio
async def test_positive_battlefy_tournament_stalker():
    from backend.stalker.battlefy import stalk_battlefy_tournament

    test_tournament = "https://battlefy.com/tectum-dachverband/tent-juni-2020/5e9733113e0a5a108788275c/info?infoTab=details"

    await stalk_battlefy_tournament(test_tournament)
