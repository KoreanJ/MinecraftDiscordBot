import discord
import requests as r
import os
import json
from bs4 import BeautifulSoup

client = discord.Client()

# Scrape requested recipe from Minecraft website
def get_recipe(item):
    url = 'https://minecraft.gamepedia.com/' + item.lower()
    req = r.get(url)
    if req.ok == False:
        print("Error connecting to {0}".format(url))
    else:
        # On load, scrape items used in recipe (first seen, not all of the options)
        soup = BeautifulSoup(req.content, 'html.parser')
        msg_list = []
        recipe_hrefs = []
        for item in soup.find('span', {'class': 'mcui mcui-Crafting_Table pixel-image'}).find_all('span', {'class': 'invslot'})[:9]:
            block = item.find('a')
            if block is None:
                recipe_hrefs.append('None')
                msg_list.append('X')
            else:
                recipe_hrefs.append(block.get('href'))
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

    if message.content.startswith('>speak'):
        await message.channel.send('Hello, this is Minecraft Bot!')

    if message.content.startswith('>recipe '):
        item = message.content[8:]
        print('Requested item: {0}'.format(item))
        msg_list = get_recipe(item)

        # Send messages in grid format to discord
        # i = 0
        # for msg in msg_list:
        #     await message.channel.send(msg)
        #     if i == 2:
        #         await message.channel.send('A\n')
        #         i = 0
        #     else:
        #         i += 1
        await message.channel.send('{0}           {1}           {2}'.format(msg_list[0], msg_list[1], msg_list[2]))
        await message.channel.send('{0}           {1}           {2}'.format(msg_list[3], msg_list[4], msg_list[5]))
        await message.channel.send('{0}           {1}           {2}'.format(msg_list[6], msg_list[7], msg_list[8]))

## Start the bot ##
token = get_bot_token()['token']
client.run(token)