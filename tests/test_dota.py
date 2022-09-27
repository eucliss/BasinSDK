from sqlite3 import connect
import pytest
from flaky import flaky
import web3
from unittest.mock import patch
from unittest.mock import Mock
from BasinSDK.dota import Dota
from dotenv import load_dotenv
import os


load_dotenv()

accountId = os.getenv('ACCOUNTID')
accountId = os.getenv('ARENAMATCH')

placeMap = ['first', 'second', 'third']

@pytest.fixture
def dota():
    return Dota()

def test_getLastMatch(dota):
    res = dota.getLastMatch(accountId)
    assert len(res.keys()) > 0
    assert res['match_id'] > 0

def test_getMatchDetails(dota):
    _id = dota.getLastMatch(accountId)['match_id']
    res = dota.getMatchDetails(_id)
    # print(res)

def test_get_arena_match_details(dota):
    res = dota.getArenaMatchDetails(arenaMatch)
    assert len(res['players']) > 0
    assert res['game_id'] == arenaMatch
    # print(res.keys())

@flaky(max_runs=3)
def test_get_arena_match_winners(dota):
    winners = dota.getArenaMatchWinners(arenaMatch)
    assert len(winners) == 3
    for i in range(0, len(winners)):
        place = placeMap[i]
        assert 'steam_id' in winners[place].keys()
        assert 'game_player_id' in winners[place].keys()
        assert 'username' in winners[place].keys()
        assert winners[place]['place'] == i + 1