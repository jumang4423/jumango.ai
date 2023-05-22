import requests
from dotenv import load_dotenv
import discord
import os
import random
from src.ai_chat.chat import chat_from_global_conv_his
from src.chroma.db import remember, recall

# env load
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

conv_his = []
MAX_LEN = 8
bot_emoji_exp = {
    "chat": "🫧",
    "memorize": "✨",
    "erase": "💨",
    "thinking": "🤔"
}

def help():
    return """```
jumango.ai help
commands:
  (echo) repeat what you say
  (<)    chat with jumango
  (<<)   remember what you say
  (*)    forget previous memory
```"""


def erase():
    conv_his = []

def random_exp():
    exps = [
        "hmm...",
        "interesting...",
        "well...",
        "i see...",
    ]

    return exps[random.randint(0, len(exps) - 1)]

class MyClient(discord.Client):
    def mention_str(self):
        return "<@{0}>".format(self.user.id)

    def add_conv_his(self, msg, userName, is_msg_from_bot):
        global conv_his
        if is_msg_from_bot and msg[:1] != bot_emoji_exp["chat"]:
            return
        if is_msg_from_bot:
            msg = msg[1:]
            conv_his.append({ 'role': 'assistant', 'content': msg })
        else:
            msg_arr = msg.split()
            if msg_arr[0] == self.mention_str():
                msg_arr = msg_arr[1:]
                if len(msg_arr) == 0:
                    msg_arr = ["how do you think?"]
            conv_his.append({ 'role': 'user', 'content': "{0}: {1}".format(userName, ' '.join(msg_arr)) })
            if len(conv_his) > MAX_LEN:
                conv_his.pop(0)

        print("conv_his: ", conv_his)


    async def on_ready(self):
        print('logged on as {0}'.format(self.user))

    async def on_message(self, message):
        is_msg_from_bot = message.author == self.user
        userName = message.author.name
        self.add_conv_his(message.content, userName, is_msg_from_bot)
        if is_msg_from_bot:
            return
        commands = message.content.split()
        if commands[0] != self.mention_str():
            return
        command = commands[1] if len(commands) > 1 else ""
        args = commands[2:] if len(commands) > 2 else []
        print('command from {0.author}: {0.content}'.format(message))

        if command == "echo":
            await message.channel.send(' '.join(args))
        elif command == "<<":
            remember(' '.join(args))
            await message.channel.send("{0} memorized".format(bot_emoji_exp["memorize"]))
        elif command == "*":
            erase()
            await message.channel.send("{0} erased".format(bot_emoji_exp["erase"]))
        elif command == "help":
            await message.channel.send(help())
        else:
            await message.channel.send("{0} {1}".format(bot_emoji_exp["thinking"], random_exp()))
            prompt = "hi jumango, " + ' '.join(commands[1:]) if len(command) != 0 else "how do you think?"
            print("prompt: ", prompt)
            bot_response = chat_from_global_conv_his(conv_his, prompt)
            await message.channel.send("{0} {1}".format(bot_emoji_exp["chat"], bot_response))

# init bot
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
