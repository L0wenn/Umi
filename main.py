import datetime
import json
import logging
import os
import traceback

from discord.ext import commands


def get_prefix(bot, message):
    prefixes = bot.config["prefixes"]

    return commands.when_mentioned_or(*prefixes)(bot, message)

bot = commands.Bot(command_prefix=get_prefix)

with open("data/config.json") as f:
    bot.config = json.load(f)
    
bot.color = 0x78DBE2
bot.launch_time = datetime.datetime.utcnow()
bot.commands_used = 0
bot.debug_mode = bot.config["debugMode"]

#setting up logging
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("discord.log", "w", "utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


if __name__ == "__main__":
    if bot.debug_mode == True:
        bot.load_extension("cogs.owner")
        bot.load_extension("cogs.errorhandler")
        bot.load_extension("cogs.eventhandler")
    else:
        for cog in os.listdir("cogs"):
            try:
                if cog.endswith(".py"):
                    bot.load_extension("cogs." + cog.replace(".py", ""))
            except:
                print(traceback.print_exc())
                continue

      
bot.run(os.environ.get("TOKEN") if not bot.debug_mode else bot.config["token"])
