import discord
import requests as r
import os
import json
import sys
from bs4 import BeautifulSoup

from discord.ext import commands

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

# Retrieve credentials for bot token and allowed admin userID
def get_bot_credentials(fname):
    if not os.path.exists(fname):
        print(fname + " does not exist")
        return None
    else:
        try:    
            with open(fname) as f:
                credentials = json.load(f)
                return credentials
        except Exception as ex:
            print("Error occurred in opening credentials file: " + ex)
            return None

# Shutdown the bot
def kill_process():
    sys.exit(0)

####################################################################

def main():
    client = commands.Bot(command_prefix=">")
    credentials = get_bot_credentials("credentials.txt")

    # If bad credentials, shutdown the bot
    if credentials is None:
        kill_process()
    # Else, register commands/events and start the bot
    else:
        token = credentials['token']
        admin_userID = credentials['admin_userID']

        # DISCORD EVENTS/COMMANDS #
        @client.command()
        async def shutdown(ctx):
            if int(ctx.author.id) == int(admin_userID):
                await ctx.send('MinecraftBot has been terminated')
                kill_process()

        @client.command()
        async def speak(ctx):
            await ctx.send('Hello, ' + ctx.author.display_name + ', this is Minecraft Bot!')

        @client.command()
        async def recipe(ctx):
            item = ctx.message.content[8:]
            print('Requested item: {0}'.format(item))
            msg_list = get_recipe(item)

            # Catch error
            if msg_list[0] == 'ERROR':
                await ctx.send(msg_list[1])
                return

            # Compile output into a table format
            title = '**' + item + '**'
            e = discord.Embed(title=title, color=0x03f8fc)
            e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[0], msg_list[3], msg_list[6]))
            e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[1], msg_list[4], msg_list[7]))
            e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[2], msg_list[5], msg_list[8]))
            await ctx.send(embed=e)

        @client.event
        async def on_message(msg):
            if msg.author == client.user:
                return
            await client.process_commands(msg)

        @client.event
        async def on_ready():
            print("=== {0.user} has been initiated ===".format(client))
            
        
        # Start the bot
        client.run(token)
    
if __name__ == "__main__":
    main()

####################################################################





