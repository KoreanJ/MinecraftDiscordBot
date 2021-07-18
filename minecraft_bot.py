import discord
import requests as r
import os
import json
import sys
import psutil as ps
import git
from bs4 import BeautifulSoup
from discord.ext import commands
from datetime import datetime


# Global Variables #
RECIPE_DIR = 'recipes'

def get_item_recipe(item_name):
    path = os.path.join(RECIPE_DIR, item_name + '.json')
    print(path)
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
            keys_items = [(x, d['key'][x]['item'].replace('minecraft:', '')) for x in d['key'].keys()]
            pattern = '\n'.join([x for x in d['pattern']])
            for key, item in keys_items:
                pattern = pattern.replace(key, item)
            pattern.replace(' ', 'X')
            return pattern
    else:
        print('error - path does not exist')

    return 'test'

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
    client.remove_command('help')
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
                log_event('shutdown()', '{0} attempted to shutdown the bot, but failed due to insufficient permissions'.format(ctx.author), 'FAILURE')
                await ctx.send('{0}, you do not have permission to use this command'.format(ctx.author))

        @client.command()
        async def status(ctx):
            if sys.platform == 'linux' and int(ctx.author.id) == int(admin_userID):
                log_event('status()', '{0} successfully got the bot status'.format(ctx.author), 'SUCCESS')
                curr_temp = ps.sensors_temperatures(fahrenheit=True)['cpu_thermal'][0][1]
                users = [x[0] for x in ps.users()]
                cpu_load = ps.cpu_percent(percpu=True)
                await ctx.send('Current Temp: ' + str(round(curr_temp,  1)) + ' °F')
                await ctx.send('Logged in User(s): ' + str(users))
                await ctx.send('CPU Load (%)' + str(cpu_load))
            else:
                log_event('status()', '{0} attempted to get bot status, but failed due to insufficient permissions'.format(ctx.author), 'FAILURE')
                await ctx.send('{0}, you do not have permission to use this command'.format(ctx.author))

        @client.command()
        async def speak(ctx):
            await ctx.send('Hello, ' + ctx.author.display_name + ', this is Minecraft Bot!')

        @client.command()
        async def help(ctx):
            await ctx.send('### How to use MinecraftBot ###\n\n>speak: MinecraftBot will say hello to you\n>status: Display MinecraftBot current temperature and logged in users (admin only)\n>recipe "item name": Prints the recipe for this item. The name must be enclosed in quotes')

        @client.command()
        async def recipe(ctx, arg):
            item = str(arg).replace(' ', '_')

            # If perfect match found, use that item. Else compile all matching item names
            matches = []
            perfect_match = False
            for fname in os.listdir(RECIPE_DIR):
                fname_item = fname.replace('.json', '')
                if item == fname_item:
                    perfect_match = True
                    matches.clear()
                    matches.append(fname_item)
                    break
                elif item in fname_item:
                    matches.append(fname_item)
            
            # Print status of recipe search
            if len(matches) <= 0:
                await ctx.send('No recipe for "{0}" was found.'.format(arg))
                return
            elif len(matches) == 1:
                if perfect_match:
                    await ctx.send('A recipe for "{0}" was found: {1}'.format(arg, matches[0]))

                    # TODO: Get recipe from file #
                    item_recipe = get_item_recipe(matches[0])
                    await ctx.send(item_recipe)
                else:
                    await ctx.send('"{0}" was found as part of another recipe: {1}\n*** If this is the recipe you want, please enter: >recipe "{1}"'.format(arg, matches[0]))
                    return
            elif len(matches) > 1:
                await ctx.send('More than 1 recipe was found for {0}.\n{1}\n*** Please enter the desired recipe using the command: >recipe "item name"'.format(arg, '\n'.join(matches)))
                return

            return

        @client.command()
        async def website_update(ctx):
            repo_path = '~/NNWedding2022'
            try:
                repo = git.Repo(repo_path)
                pull_info = repo.remotes.origin.pull()
                await ctx.send('Successfully pulled changes from repo located at "{0}"'.format(repo_path))
            except Exception as ex:
                log_event('website_update', '{0} error occurred while trying to pull git repo at "{1}"'.format(ex, repo_path), 'FAILURE')
                return

        @client.command()
        async def website_log(ctx):
            log_path = '/var/log/nginx/access.log'
            if os.path.exists(log_path):
                with open(log_path) as file:
                    max_line_cnt = 5
                    idx = 1
                    out = ''
                    for line in file.readlines():
                        if idx > 5:
                            await ctx.send(out)
                            await ctx.send('>>> End of log. Printed {0} lines. <<<'.format(max_line_cnt))
                            break
                        out += line + '\n'
                        idx += 1
            
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





