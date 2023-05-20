import requests
from dotenv import load_dotenv
import discord
import os
from src.ai_chat.chat import chat_response

# env load
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    def mention_str(self):
        return "<@{0}>".format(self.user.id)

    async def on_ready(self):
        print('logged on as {0}'.format(self.user))

    async def on_message(self, message):
        print(self.mention_str())
        if message.author == self.user:
            return
        commands = message.content.split()
        if commands[0] != self.mention_str():
            return
        command = commands[1]
        args = commands[2:]
        print('command from {0.author}: {0.content}'.format(message))

        if command == "echo":
            await message.channel.send(' '.join(args))
        elif command == "<":
            bot_response = chat_response(' '.join(args))
            await message.channel.send(bot_response)

# init bot
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
