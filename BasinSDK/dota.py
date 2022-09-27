from nis import match
from unittest import result
from dotenv import load_dotenv
import os
import requests
import json
import re
from bs4 import BeautifulSoup


load_dotenv()

OPENDOTA = os.getenv('OPENDOTA')
# ACCOUNTID = os.getenv('ACCOUNTID')


class Dota():

    def __init__(self, openDotaURL=OPENDOTA):
        self.baseURL = openDotaURL

    def getLastMatch(self, accountId):
        params = {
            'limit': 1
        }
        url = f'{self.baseURL}/players/{accountId}/matches'
        res = requests.get(url, params=params)
        return json.loads(res.content)[0]

    def getMatchDetails(self, matchId):
        res = requests.get(f'{self.baseURL}/matches/{matchId}')
        return json.loads(res.content)


    def getArenaMatchDetails(self, matchId):
        page = f'https://www.abilityarena.com/api/games/{matchId}'
        return requests.get(page).json()

    def getArenaMatchWinners(self, matchId):
        json = self.getArenaMatchDetails(matchId)
        # print(json)
        winners = {}
        for player in json['players']:
            if player['place'] == 1:
                winners['first'] = {
                    'steam_id': player['steam_id'],
                    'place': 1,
                    'game_player_id': player['game_player_id'],
                    'username': player['username']
                }
            elif player['place'] == 2:
                winners['second'] = {
                    'steam_id': player['steam_id'],
                    'place': 2,
                    'game_player_id': player['game_player_id'],
                    'username': player['username']
                }
            elif player['place'] == 3:
                winners['third'] = {
                    'steam_id': player['steam_id'],
                    'place': 3,
                    'game_player_id': player['game_player_id'],
                    'username': player['username']
                }
            else:
                continue
        return winners