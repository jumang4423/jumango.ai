import requests
from dotenv import load_dotenv
import discord
import os
import random
from src.ai_chat.chat import chat_from_global_conv_his,  is_msg_spam
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
    "thinking": "🤔",
    "spam": "🚫",
}

def help():
    return """```
jumango.ai help
commands:
    ()     chat with jumango
    (<<)   remember what you say
    (*)    forget previous memory
    (echo) repeat what you say
    (help) show this message
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

def mention_str(user_id):
    return "<@{0}>".format(user_id)

class JumangoAIBot(discord.Client):
    def mention_str(self):
        return mention_str(self.user.id)

    def add_conv_his(self, msg, userName, is_msg_from_bot):
        global conv_his
        MAX_WORD_LEN = 64
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
            # if msg is too long, split it
            if len(msg_arr) > MAX_WORD_LEN:
                msg_arr = msg_arr[:MAX_WORD_LEN]
            conv_his.append({ 'role': 'user', 'content': "{0}: {1}".format(userName, ' '.join(msg_arr)) })
            if len(conv_his) > MAX_LEN:
                conv_his.pop(0)

    async def send_alert_msg(self, msg, userID):
        channel_id = 1109401858348425256
        channel = self.get_channel(channel_id)
        await channel.send("{0} spam detected: {1} {2}".format(bot_emoji_exp["spam"], mention_str(userID), msg))

    async def on_ready(self):
        print('logged on as {0}'.format(self.user))

    async def on_message(self, message):
        is_msg_from_bot = message.author == self.user
        userName = message.author.name
        is_spam = is_msg_spam(message.content)
        if is_spam and not is_msg_from_bot:
            # if message is spam, notify to # logs channel
            await self.send_alert_msg(message.content, message.author.id)
        self.add_conv_his(message.content, userName, is_msg_from_bot)
        if is_msg_from_bot:
            return
        commands = message.content.split()
        if commands[0] != self.mention_str():
            return
        command = commands[1] if len(commands) > 1 else ""
        args = commands[2:] if len(commands) > 2 else []
        print('ai trrigered: {0}'.format(message.content[1:]))
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
            prompt = "hi jumango.ai, " + ' '.join(commands[1:]) if len(command) != 0 else "how do you think?"
            bot_response = chat_from_global_conv_his(conv_his, prompt)
            await message.channel.send("{0} {1}".format(bot_emoji_exp["chat"], bot_response))

# init bot
intents = discord.Intents.default()
intents.message_content = True
client = JumangoAIBot(intents=intents)
