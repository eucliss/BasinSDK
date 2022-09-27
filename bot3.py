# This example requires the 'members' privileged intent to use the Member converter
# and the 'message_content' privileged intent for prefixed commands.

from email.errors import CloseBoundaryNotFoundDefect
import random
from typing_extensions import get_overloads

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from BasinSDK import connector

description = """
An example bot to showcase the discord.ext.commands extension module.
There are a number of utility commands being showcased here.
"""

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description=description, intents=intents)

connector = connector.Connector()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

# @bot.event
# async def on_message(ctx: commands.Context):
#     print(f'Message from {ctx.author}: {ctx.content}, {ctx}')
#     print(ctx.channel.id)


@bot.command()
async def register(ctx: commands.Context, steamId: str):
    """"Register a user in the database and assign them a wallet"""
    # res = connector.register(ctx, steamId)
    res = connector.register(str(ctx.author), str(steamId))
    if res == False:
        await ctx.send('Already registered.')
    else:
        await ctx.send(f'Registered {res["discordName"]}')

@bot.command()
async def restart(ctx: commands.Context):
    res = connector.restart()
    if res:
        await ctx.send(f'Successfully restarted')
    else:
        await ctx.send(f'ERROR')
    

@bot.command()
async def create(ctx: commands.Context):
    res = connector.createTournament(str(ctx.author))
    await ctx.send(f'Successfully created tournament with ID: {res}')
    
@bot.command()
async def join(ctx: commands.Context, _id: int):
    res = connector.joinTournament(str(ctx.author), _id)
    await ctx.send(f'Successfully joined tournament: {_id}')
    await ctx.send(f'Tournament Participants: {res}')

@bot.command()
async def start(ctx: commands.Context, _id: int):
    status, mes = connector.startTournament(str(ctx.author), _id)
    if status == 200:
        await ctx.send(mes)
    else:
        await ctx.send(f'{mes}')

@bot.command()
async def cancel(ctx: commands.Context, _id: int):
    status, mes = connector.cancelTournament(str(ctx.author), _id)
    if status == 200:
        await ctx.send(mes)
    else:
        await ctx.send(f'{mes}')
    

@bot.command()
async def finish(ctx: commands.Context, _id: int, matchId):
    status, mes, results = connector.finishTournament(str(ctx.author), _id, matchId)
    if status == 200:
        await ctx.send(mes)
        await ctx.send('Updated Results:')
        print(len(results))
        print(results)
        for i in range(0, len(results)):
            item = results[i]
            await ctx.send(f'{i + 1} Place: {item["name"]} with updated balance: {item["balance"]} and wins: {item["wins"]}')

    else:
        await ctx.send(f'{mes}')

# Now we need to close it
# this is the hard part
# we gotta:

# 1. Set the status of the tournament to CLOSED 
# 2. Maybe add the winner of the tournament to the DB 
# 3. Add points to that winners balance

# Then we gotta connect to the blockchain. Probably also refactor at some point
# This code is a shit mess 
# but its actually pretty good 
# So we'll gotta add a ERC20 smart contract to start then we can create an 
# orgranizer account in the test net and fill it with ether 
# Add that account this the DB so we can hook it whenever
# then hook up the app to web3 
# we need to create the tournament 
# add all the shit to the payouts and players and shit
# and go through the motions
# starting and closing will initiate the first transactions 
# then we'll eliminate all players over time
# etc.

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

bot.run(token)