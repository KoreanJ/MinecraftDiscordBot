import discord
import requests as r
import os
import json
import sys
import psutil as ps
from bs4 import BeautifulSoup
from discord.ext import commands
from datetime import datetime

# Scrape requested recipe from Minecraft website
def get_recipe(item):
    url = 'https://minecraft.gamepedia.com/' + item.lower()
    req = r.get(url)
    if req.ok == False:
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

# Report system status
def system_status():
    return 

# Log events
def log_event(method_name, event, status):
    f_name = 'log.txt'
    event_time = datetime.now().strftime('%m/%d/%y %H:%M:%S')
    with open(f_name, 'a+') as f:
        f.write('[{0}, {1}, {2}, {3}]\n'.format(str(event_time), method_name, event, status))
    return

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
                log_event('shutdown()', '{0} successfully shutdown the bot'.format(ctx.author), 'SUCCESS')
                await ctx.send('MinecraftBot has been terminated')
                await client.logout()
            else:
                log_event('shutdown()', '{0} attempted to shutdown the bot, but failed'.format(ctx), 'FAILURE')


        @client.command()
        async def status(ctx):
            if sys.platform == 'linux' and int(ctx.author.id) == int(admin_userID):
                curr_temp = ps.sensors_temperatures(fahrenheit=True)['cpu_thermal'][0][1]
                users = [x[0] for x in ps.users()]
                cpu_load = ps.cpu_percent(percpu=True)
                await ctx.send('Current Temp: ' + str(round(curr_temp,  1)) + ' °F')
                await ctx.send('Logged in User(s): ' + str(users))
                await ctx.send('CPU Load (%)' + str(cpu_load))

        @client.command()
        async def speak(ctx):
            await ctx.send('Hello, ' + ctx.author.display_name + ', this is Minecraft Bot!')

        @client.command()
        async def recipe(ctx, arg):
            try: 
                item = arg
                msg_list = get_recipe(item)
                log_event('recipe()', '{0} requested recipe for "{1}"'.format(ctx.author, item), 'SUCCESS')

                # Catch error
                if msg_list[0] == 'ERROR':
                    log_event('recipe()', '{0}: Unable to retrieve recipe for "{1}"'.format(ctx.author, item), 'FAILURE')
                    await ctx.send(msg_list[1])
                    return

                # Compile output into a table format
                title = '**' + item + '**'
                e = discord.Embed(title=title, color=0x03f8fc)
                e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[0], msg_list[3], msg_list[6]))
                e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[1], msg_list[4], msg_list[7]))
                e.add_field(name='----', value='{0}\n{1}\n{2}'.format(msg_list[2], msg_list[5], msg_list[8]))
                await ctx.send(embed=e)
            except Exception as ex:
                log_event('recipe()', '{0}: Exception occurred while requesting "{1}": {2}'.format(ctx.author, item, ex), 'FAILURE')
                await ctx.send('Unable to get recipe for the requested item "{0}": '.format(item))
                return

        @client.event
        async def on_message(msg):
            if msg.author == client.user:
                return
            await client.process_commands(msg)

        @client.event
        async def on_ready():
            log_event('main()', '{0} has successfully been initialized'.format(client.user), 'SUCCESS')
            
        
        # Start the bot
        client.loop.run_until_complete(client.start(token))
    
if __name__ == "__main__":
    main()

####################################################################





