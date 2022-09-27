# BASIN DISCORD BOT

To run the bot:
`python bot3.py`

To run the testing script:

`python testing.py`

To start the DB:
`brew services start mongodb-community@6.0`
or
`make mongodb-start`

To stop the DB:
`brew services stop mongodb-community@6.0`
or 
`make mongodb-stop`

If you're having issues where BasinSDK cant be found:
```
TOPDIR=${pwd}
export PYTHONPATH=${PYTHONPATH}:${TOPDIR}
```

Resources:
```
https://realpython.com/introduction-to-mongodb-and-python/
https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-os-x/
```

Tasks:
- [x] Bot is connected to discord
- [] Bot has a channel that is only for tournaments
- [x] User can *Register* their discord account to receive a wallet on the test net - provisioned by the bot
- [x] User can then create a tournament (the tournament itself will be hardcoded, uncertain what the metric will be)
    1. thinking something like we have people playing dota 
    2. so what can we bet on 
    3. I think damage is probably a good metric and also KDA
    4. We will also need the persons steam account or something for auto getting the ranks
- [x] tournament is now created and open for registration
- [x] A user must then join the tournament
- [] User wagers X amount on the tournament
- [x] Creator can cancel the tournament if needed
- [] User plays game of dota
- [] User closes the tournament and the bot scans the creators profile for last played game and gets the stats

MVP:
Me and my friends can log into discord, create a tournament in the chat, so get wallets, register, create a tournament from a main account, play a game of dota, and finish the tournament when the game of dota is done.