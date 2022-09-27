from shutil import ExecError
import web3
import json
import time
import random
from dotenv import load_dotenv
import os
from BasinSDK.db import MongoDB
from BasinSDK.dota import Dota

load_dotenv()

token = os.getenv('INFURA_KEY')
BASIN = os.getenv('BASIN')


class Connector():

    def __init__(self, BasinAddress=BASIN, abi=None, database='BasinSDK', collection='Wallets', tournamentCollection='Tournaments', organizer=''):
        
        self.organizer = organizer
        self.client = MongoDB()
        self.databaseName = database
        self.collectionName = collection
        self.db = self.client.setDatabase(database)
        self.collection = self.client.setCollection(collection)
        self.tournamentCollection = tournamentCollection

        # self.w3 = web3.Web3(web3.HTTPProvider(f'https://rinkeby.infura.io/v3/{token}'))
        self.w3 = web3.Web3(web3.HTTPProvider('http://127.0.0.1:8545'))
        if not self.w3.isConnected():
            print("Error loading web3 connection")
        self.version = self.w3.clientVersion
        self.basinAddress = BasinAddress
        self.abi = abi
        self.attachContract()
        self.tournamentId = 1

        # self.deployer = self.w3.eth.accounts[0] #"0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        # self.player2 = self.w3.eth.accounts[1] # "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
        # self.owner = self.w3.eth.accounts[2]
        # self.payouts = [1000000, 0]
        # self.players = [self.deployer, self.player2]
        # if abi == None:
        #     with open('./abi/TournamentsFactory.sol/TournamentsFactory.json') as json_file:
        #         data = json.load(json_file)
        #     self.abi = data['abi']
        # else:
        #     self.abi = abi

        # self.contract = self.w3.eth.contract(address=self.factoryAddress, abi=self.abi)
        # balance = self.w3.eth.getBalance("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")

    def attachContract(self):
        if self.abi == None:
            with open('./abi/IBasin.json') as json_file:
                data = json.load(json_file)
            self.abi = data['abi']
        self.contract = self.w3.eth.contract(address=self.basinAddress, abi=self.abi)
        return self.contract
    
    def restart(self):
        self.client.kill()
        return True

    def register(self, author, steamId):
        recs = self.client.getRecord({'discordName': author}, db=self.databaseName, collection=self.collectionName)
        if len(recs) > 0:
            self.client.kill()
            return 
        # acc = self.w3.eth.account.create()
        obj = {
            'discordName': author,
            'steamId': str(steamId),
            'address': '0', #acc.address,
            'key': '0', #acc.key,
            'privateKey': '0', # acc.privateKey,
            'balance': 0,
            'wins': 0,
            'losses': 0
        }
        self.client.storeRecord(obj, self.databaseName, self.collectionName)
        return obj

    def createTournament(self, author):
        obj = {
            'creator': author,
            'participants': list(),
            'id': self.tournamentId,
            'status': 'OPEN',
            'winners': {},
            'matchId': ''
        }
        self.tournamentId = self.tournamentId + 1
        self.client.storeRecord(obj, self.databaseName, self.tournamentCollection)
        return self.tournamentId - 1
    
    def joinTournament(self, author, tournamentId: int):
        tFilter = {"id": tournamentId}
        record = self.client.getRecord(tFilter, db=self.databaseName, collection=self.tournamentCollection)
        if 'OPEN' != record[0]['status']:
            # Replace this with an error
            return 'FAILED TO JOIN, TOURNAMENT IN PROGRESS'
        if author in record[0]['participants']:
            return record[0]['participants']
        newParticipants = record[0]['participants']
        newParticipants.append(author)
        self.client.updateRecord(
            tFilter,
            {'participants': newParticipants},
            db=self.databaseName,
            collection=self.tournamentCollection
        )
        return newParticipants
    
    def startTournament(self, author, tournamentId: int):
        tFilter = {"id": tournamentId}
        record = self.client.getRecord(tFilter, db=self.databaseName, collection=self.tournamentCollection)
        if author != record[0]['creator']:
            return 400, "Not your tournament"
        if 'OPEN' != record[0]['status']:
            return 420, "Tournament not open"    
        self.client.updateRecord(
            tFilter,
            {'status': 'IN PROGRESS'},
            db=self.databaseName,
            collection=self.tournamentCollection
        )
        return 200, "Tournament now in progress, no new joiners."
    
    def cancelTournament(self, author, tournamentId: int):
        tFilter = {"id": tournamentId}
        record = self.client.getRecord(tFilter, db=self.databaseName, collection=self.tournamentCollection)
        if author != record[0]['creator']:
            return 400, "Not your tournament"
        self.client.updateRecord(
            tFilter,
            {'status': 'CANCELLED'},
            db=self.databaseName,
            collection=self.tournamentCollection
        )
        return 200, "Tournament cancelled"
        

    def finishTournament(self, author, tournamentId: int, matchId):
        # 1. Set the status of the tournament to CLOSED 
        # 2. Maybe add the winner of the tournament to the DB 
        # 3. Add points to that winners balance
        try: 
            tFilter = {"id": tournamentId}
            record = self.client.getRecord(tFilter, db=self.databaseName, collection=self.tournamentCollection)
            print('got a record')
            if author != record[0]['creator']:
                return 400, "Not your tournament", ''
            if 'IN PROGRESS' != record[0]['status']:
                return 420, "Tournament still open", ''   

            dota = Dota()
            winners = dota.getArenaMatchWinners(matchId)
            print(f'got winners {winners}')
            self.client.updateRecord(
                tFilter,
                {
                    'status': 'CLOSED',
                    'matchId': matchId,
                    'winners': winners
                },
                db=self.databaseName,
                collection=self.tournamentCollection
            )

            print('DB updated')
            # we gotta do the dota shit here 
            results = self.distributeWinnings(
                tournamentId,
                winners,
                db = self.databaseName,
                collection = self.collectionName
            )
            print(results)
            print('buh')
        except Exception as e:
            return 400, f'Tournament failed with error: {e}', 'ERROR'

        return 200, "Tournament status updated", results

    def distributeWinnings(self, tournamentId: int, winners, db=None, collection=None):
        first = winners['first']
        if db == None:
            db = self.databaseName
        if collection == None:
            collection = self.collectionName
        res = []
        print(first)
        records = self.client.getRecord({'steamId': first['steam_id']}, db=str(db), collection=str(collection))
        print(f'got first records {records}')
        if len(records) > 0:
            self.client.updateRecord(
                {'steamId': first['steam_id']},
                {
                    'balance': records[0]['balance'] + 100,
                    'wins': records[0]['wins'] + 1,
                }
            )
            res.append({
                'name': first['username'],
                'wins': records[0]['wins'] + 1,
                'balance': records[0]['balance'] + 100
            })

            # Execute smart contract here
        
        second = winners['second']
        records = self.client.getRecord({'steamId': second['steam_id']}, db=str(db), collection=str(collection))
        print(f'got second records {records}')

        if len(records) > 0:
            self.client.updateRecord(
                {'steamId': second['steam_id']},
                {
                    'balance': records[0]['balance'] + 50,
                }
            )
            res.append({
                'name': second['username'],
                'wins': records[0]['wins'],
                'balance': records[0]['balance'] + 50
            })

            # Execute smart contract here
        
        third = winners['third']
        records = self.client.getRecord({'steamId': third['steam_id']}, db=str(db), collection=str(collection))
        if len(records) > 0:
            self.client.updateRecord(
                {'steamId': third['steam_id']},
                {
                    'balance': records[0]['balance'] + 10,
                }
            )
            res.append({
                'name': third['username'],
                'wins': records[0]['wins'],
                'balance': records[0]['balance'] + 10
            })

        
        return res




        



    # def go(self):
    #     tournamentAddress = self.createTournament(self.players, self.payouts, 0, self.owner)
    #     self.startTournament(tournamentAddress)
    #     winner = self.getRandomWinner(self.players)
    #     if winner == self.player2:
    #         self.eliminatePlayer(
    #             tournamentAddress,
    #             winner,
    #             1
    #         )
    #         self.eliminatePlayer(
    #             tournamentAddress,
    #             self.deployer,
    #             2
    #         )
    #     else:
    #         self.eliminatePlayer(
    #             tournamentAddress,
    #             winner,
    #             1
    #         )
    #         self.eliminatePlayer(
    #             tournamentAddress,
    #             self.player2,
    #             2
    #         )
    #     self.completeTournament(tournamentAddress)
    #     print(
    #     f"""
    #         RESULTS:
    #         WINNER: {winner}
    #     """)
    #     return winner

    #     # self.eliminatePlayer(
    #     #     tournamentAddress,
    #     #     self.player2,
    #     #     2
    #     # )

    # def getRandomWinner(self, players):
    #     # rand = random(0, len(players))
    #     rand = random.randint(0, len(players)) - 1
    #     rand = 0
    #     return players[rand]

    # def completeTournament(self, tournamentAddress):
    #     tx_hash = self.contract.functions.completeTournament(
    #         tournamentAddress,
    #         self.players,
    #         self.payouts,
    #         0
    #     ).transact({'from': self.owner})


    # def getTournamentAddressFromTxHash(self, tx_hash):
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
    #     return tx_receipt.logs[0].address

    # def createTournament(self, players, payouts, distributorFee, controller):
    #     tx_hash = self.contract.functions.createTournament(
    #         players,
    #         self.payouts,
    #         0,
    #         self.owner
    #     ).transact({'from': self.owner, 'value': 100000000000000000000})
    #     tournamentAddress = self.getTournamentAddressFromTxHash(tx_hash)
    #     return tournamentAddress

    # def startTournament(self, tournamentAddress):
    #     tx_hash = self.contract.functions.startTournament(
    #         tournamentAddress,
    #         self.players,
    #         self.payouts,
    #         0
    #     ).transact({'from': self.owner})
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

    #     print(str(self.contract.functions.tournaments("0xa1C033fb2037b592F3a222EFE876457b10349597").call()))
    #     print(str(self.contract.functions.tournaments(tournamentAddress).call()))
    #     print("Tournament Started")

    # def eliminatePlayer(self, tournamentAddress, player, place):
    #     tx_hash = self.contract.functions.eliminatePlayer(
    #         tournamentAddress,
    #         self.players,
    #         self.payouts,
    #         0,
    #         player,
    #         place
    #     ).transact({'from': self.owner})
    #     tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
    #     print(tx_receipt)
    #     print("Player Eliminated")


connector = Connector()