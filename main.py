import discord
from discord.ext import commands, tasks
import json
import os


client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if(message.content.startswith('!hello')):
        author = str(message.author)
        resp = "Hello " + author[:-5]
        await message.channel.send(resp)


client = commands.Bot(command_prefix=os.getenv('DISCORD_BOT_PREFIX'), case_insensitive=True)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

@client.event
async def on_ready():
    activity = os.getenv('DISCORD_ACTIVITY') or 'Minecraft'
    await client.change_presence(activity=discord.Game(name=activity))

client.run(os.getenv('DISCORD_BOT_TOKEN'))
