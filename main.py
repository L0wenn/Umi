import datetime
import logging
import os
import traceback
from datetime import datetime
from sys import version as sv

import discord
import pymongo
from discord import Game
from discord import __version__ as dv
from discord.ext import commands
from dotenv import load_dotenv
from pymongo.errors import CollectionInvalid, DuplicateKeyError


async def get_prefix(bot, message):
    # Long story short, this function didn't want to work.
    # Only because i put : afer the _id in find_one() function
    # and ofc because _id: field doesn't exist it always returned None 
    # I've wasted 8 hours of my life because i couldn't see it
    return commands.when_mentioned_or(bot.db.settings.find_one({"_id": message.guild.id})["prefix"])(bot, message)
    
bot = commands.Bot(command_prefix=get_prefix,
                    case_insensitive = True, intents = discord.Intents.all(),
                    activity=Game(name="Searching for the library (m!help)"))

load_dotenv()
MONGODB_URI = os.environ.get("MONGODB_URI")
client = pymongo.MongoClient(MONGODB_URI)
debug_mode = True

bot.db = client["Mint"]
bot.color = 0x98ff98
bot.launch_time = datetime.utcnow()
bot.commands_used = 0

#setting up logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("discord.log", "w", "utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
    global_users = bot.db["global"]
    bot_settings = bot.db.settings

    for guild in bot.guilds:
        # create guild collection if doesn't exist
        try:
            bot.db.create_collection(str(guild.id))
        except CollectionInvalid: # means that the collection already exists
            pass

        guild_settings = {
            "_id"           :   guild.id,
            "prefix"        :   "m!",
            "logChannel"    :   None,
            "muteRoleID"    :   None,
            "welcomeChannel":   None,
            "welcomeMessage":   "Welcome to ?g, Dr. ?n",
            "warnAction"    :   False,
            "warnLimit"     :   3
        }

        # create guild in settings collection
        try:
            bot_settings.insert_one(guild_settings)
        except DuplicateKeyError: # means that the guild already exists in the collection
            pass

        for member in guild.members:
            if member.bot:
                continue

            global_user = {
                "_id"        :    member.id,
                "rep"        :    0,
                "desc"       :    None,
                "repTime"    :    datetime(2000, 1, 1, 1, 1, 1, 1),
                "pocket"     :    0,
                "bank"       :    0,
                "dailyTime"  :    datetime(2000, 1, 1, 1, 1, 1, 1),
                "dailyStreak":    0,
                "lvlupbg"    :    None,
                "profilebg"  :    None,
                "dispTitle"  :    None
            }
            guild_member = {
                "_id"         :   member.id,
                "level"       :   1,
                "exp"         :   0,
                "nextLevelExp":   36,
                "warns"       :   []
            }

            #basically doing the same as above
            try:
                global_users.insert_one(global_user)
            except DuplicateKeyError:
                pass

            try:
                guild_coll = bot.db[str(guild.id)]
                guild_coll.insert_one(guild_member)
            except DuplicateKeyError:
                pass

    print("Bot online and ready to work!")
    print("-----------------------------")
    print(f"Running on Python {sv[:5]}")
    print(f"discord.py ver: {dv}")
    print(f"Mode: {'DEV' if debug_mode else 'Stable'}")
    print("-----------------------------")


if __name__ == "__main__":
    if debug_mode == True:
        bot.load_extension("cogs.owner")
        bot.load_extension("cogs.errorhandler")
        bot.load_extension("cogs.eventhandler")
    else:
        for cog in os.listdir("Mint/cogs"):
            try:
                if cog.endswith(".py"):
                    bot.load_extension("cogs." + cog.replace(".py", ""))
            except:
                print(traceback.print_exc())
                continue

bot.run(os.environ.get("TOKEN")) 
