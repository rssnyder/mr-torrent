import discord
from discord.ext import commands, tasks
import json
import os

def load_json(token):
    with open('./config.json') as f:
        config = json.load(f)
    return config.get(token)

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(message.content.startswith('!hello')):
        author = str(message.author)
        resp = "Hello " + author[:-5]
        await message.channel.send(resp)


client = commands.Bot(command_prefix=load_json('prefix'), case_insensitive=True)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(os.getenv('DISCORD_BOT_TOKEN'))
