from dataclasses import dataclass
from sqlite3 import connect
from typing import Collection
import pytest
import web3
from unittest.mock import patch
from unittest.mock import Mock
from BasinSDK.connector import Connector

DATABASE_NAME='testing-connector'
COLLECTION_NAME='test-connector'
TOURNAMENTS_COLLECTION='test-tournament-collection'

tournamentId = 1

author = 'test'

def kill(connector):
    connector.client.setDatabase(DATABASE_NAME)
    connector.client.setCollection(COLLECTION_NAME)
    connector.client.collection.drop()

def mockCTX(author='test'):
    mock = Mock()
    mock.author.name = author
    return mock

def populateDB(connector):
    for i in range(1, 4):
        obj = {
            'discordName': f'discord{i}',
            'steamId': f'id_{i}',
            'address': '0x0',
            'key': '',
            'privateKey': '',
            'balance': 0,
            'wins': 0,
            'losses': 0
        }
        connector.client.storeRecord(obj, db=DATABASE_NAME, collection=COLLECTION_NAME)

def setupMockWinners(connector):
    winners = {}
    winners['first'] = {
        'steam_id': 'id_1',
        'place': 1,
        'game_player_id': 'game_id_1',
        'username': 'username_1'
    }
    winners['second'] = {
        'steam_id': 'id_2',
        'place': 2,
        'game_player_id': 'game_id_2',
        'username': 'username_2'
    }
    winners['third'] = {
        'steam_id': 'id_3',
        'place': 3,
        'game_player_id': 'game_id_3',
        'username': 'username_3'
    }
    populateDB(connector)
    return winners
    

def mockAccount():
    mock = Mock()
    mock.address = '0x0'
    mock.key = 'key'
    mock.privateKey = 'privateKey'
    return mock

@pytest.fixture
def connector():
    return Connector(database=DATABASE_NAME, collection=COLLECTION_NAME, tournamentCollection=TOURNAMENTS_COLLECTION)

def wipeDB(connector):
    connector.client.setDatabase(DATABASE_NAME)
    connector.client.setCollection(TOURNAMENTS_COLLECTION)
    connector.client.collection.drop()


# @patch('BasinSDK.connector.web3.eth', return_value = mockAccount())
# def test_register(connector):
#     obj = connector.register(mockCTX())
#     assert obj['discordName'] == mockCTX().author
#     assert '0x' in obj['address']
#     assert obj["balance"] == 0


def test_attach(connector):
    res = connector.attachContract()
    assert 'deliverPackages' in res.functions
    assert 'toggleFee' in res.functions

def test_create_tournament(connector):
    wipeDB(connector)
    res = connector.createTournament(author)
    assert res == tournamentId
    records = connector.client.getRecord({'id': res}, db=DATABASE_NAME, collection=TOURNAMENTS_COLLECTION)
    assert len(records) == 1
    assert records[0]['creator'] == author

def test_create_tournament(connector):
    wipeDB(connector)
    res = connector.createTournament(author)
    assert res == tournamentId
    res = connector.createTournament(author)
    assert res == tournamentId + 1

def test_join_tournament(connector):
    res = connector.joinTournament('player1', tournamentId)
    records = connector.client.getRecord({'id': tournamentId}, db=DATABASE_NAME, collection=TOURNAMENTS_COLLECTION)
    assert len(records) == 1
    assert records[0]['participants'] == ['player1']

def test_start_tournament(connector):
    status, mes = connector.startTournament(author, tournamentId)
    records = connector.client.getRecord({'id': tournamentId}, db=DATABASE_NAME, collection=TOURNAMENTS_COLLECTION)
    assert status == 200
    assert mes == "Tournament now in progress, no new joiners."
    assert records[0]['status'] == 'IN PROGRESS'

def test_cancel_tournament(connector):
    status, mes = connector.cancelTournament(author, tournamentId)
    records = connector.client.getRecord({'id': tournamentId}, db=DATABASE_NAME, collection=TOURNAMENTS_COLLECTION)
    assert status == 200
    assert mes == "Tournament cancelled"
    assert records[0]['status'] == 'CANCELLED'

def testDistributeWinnings(connector):
    kill(connector)
    winners = setupMockWinners(connector)
    res = connector.distributeWinnings(tournamentId, winners)

    #first 
    first = res[0]
    assert first['balance'] == 100
    assert first['wins'] == 1
    assert first['name'] == 'username_1'

    #second
    second = res[1]
    assert second['balance'] == 50
    assert second['wins'] == 0
    assert second['name'] == 'username_2'

    #third
    third = res[2]
    assert third['balance'] == 10
    assert third['wins'] == 0
    assert third['name'] == 'username_3'






# <Message id=1021211350913007676 channel=<TextChannel id=1020726837757878382 name='dev' position=5 nsfw=False category_id=887737654127517717 news=False> type=<MessageType.default: 0> author=<Member id=73867181204451328 name='Smig' discriminator='0682' bot=False nick='waint' guild=<Guild id=887737654127517716 name='waint cord' shard_id=0 chunked=False member_count=3>> flags=<MessageFlags value=0>>