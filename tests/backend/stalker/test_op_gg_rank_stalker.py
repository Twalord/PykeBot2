import pytest


@pytest.mark.asyncio
async def test_positive_stalk_player_op_gg():
    from backend.stalker import op_gg_rank
    from models.data_models import Player, Rank

    test_player = Player("UFF NiceToMeetMe")

    test_rank = Rank(rank_string=await op_gg_rank.stalk_player_op_gg(test_player.summoner_name))

    assert str(test_rank) == "Platinum 1"

# full test is part of test_prime_league to avoid stalking primeleague.gg twice

@pytest.mark.asyncio
async def test_positive_stalk_player_riot_api():
    from backend.stalker import riot_api_rank
    from models.data_models import Player, Rank

    test_player = Player("UFF NiceToMeetMe")

    test_rank = Rank(rank_string=await riot_api_rank.stalk_player_riot_api(test_player.summoner_name))

    assert str(test_rank) == "Platinum 1"
