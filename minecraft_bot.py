import discord
import requests as r
import os
import json
import sys
from bs4 import BeautifulSoup

client = discord.Client()

# Scrape requested recipe from Minecraft website
def get_recipe(item):
    url = 'https://minecraft.gamepedia.com/' + item.lower()
    req = r.get(url)
    if req.ok == False:
        print("Error connecting to {0}".format(url))
        return ['ERROR', 'A recipe for "' + item + '" was not found on ' + url]
    else:
        # On load, scrape items used in recipe (first seen, not all of the options)
        soup = BeautifulSoup(req.content, 'html.parser')
        msg_list = []

        # Find crafting table data, exit if not found
        crafting_table = soup.find('span', {'class': 'mcui mcui-Crafting_Table pixel-image'})
        if crafting_table is None:
            return ['ERROR', 'The item "' + item + '" has no crafting recipe. Maybe this is an ingredient?']

        # Get name of each item in crafting recipe
        for item in crafting_table.find_all('span', {'class': 'invslot'})[:9]:
            block = item.find('a')
            if block is None:
                msg_list.append('.')
            else:
                msg_list.append(block.get('href')[1:])
    
    return msg_list

# Open token from file
def get_bot_token():
    with open('token.txt') as f:
        token = json.load(f)

    return token

@client.event
async def on_ready():
    print("=== {0.user} has been initiated ===".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == '>speak':
        await message.channel.send('Hello, ' + message.author.display_name + ', this is Minecraft Bot!')

    if message.content == '>kill':
        await message.channel.send('<MinecraftBot has disconnected>')
        os._exit(0)

    if message.content.startswith('>recipe '):
        item = message.content[8:]
        print('Requested item: {0}'.format(item))
        msg_list = get_recipe(item)

        # Catch error
        if msg_list[0] == 'ERROR':
            await message.channel.send(msg_list[1])
            return

        # Compile output into a table format
        title = '**' + item + '**'
        e = discord.Embed(title=title, color=0x03f8fc)
        e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[0], msg_list[3], msg_list[6]))
        e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[1], msg_list[4], msg_list[7]))
        e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[2], msg_list[5], msg_list[8]))
        await message.channel.send(embed=e)

## Start the bot ##
token = get_bot_token()['token']
client.run(token)