import discord
import requests as r
import os
import json
from bs4 import BeautifulSoup as soup

client = discord.Client()

# Scrape requested recipe from Minecraft website
def get_recipe(item):
    url = 'https://minecraft.gamepedia.com/' + item.lower()
    req = r.get(url)
    if req.ok == False:
        print("Error connecting to {0}".format(url))
        return "ERROR"
    else:
        print("Successful connection to {0}".format(url))
        return "SUCCESS"

# Open token from file
def get_bot_token():
    with open('token.txt') as f:
        return json.load(f)

@client.event
async def on_ready():
    print("Hello, this is {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('>speak'):
        await message.channel.send('Hello, this is Minecraft Bot!')

    if message.content.startswith('>recipe '):
        item = message.content[8:]
        print('Requested item: {0}'.format(item))
        status = get_recipe(item)
        await message.channel.send(status)

## Start the bot ##
client.run(get_bot_token())