from email.message import Message
import discord
from helpers.message_parse import MessageParser
from dotenv import load_dotenv
import os
import BasinSDK


class MyClient(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        mp = MessageParser()
        print(f'Message from {message.author}: {message.content}, {message}')
        mp.parseMessage(message)

load_dotenv()

token = os.getenv('DISCORD_TOKEN')

client = MyClient()
client.run(token)