import typing
from random import randint
from datetime import datetime

import discord
import pymongo
from discord.ext import commands
from discord.ext.commands import Cog

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self._cd = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        """Returns the ratelimit left"""
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()


    async def __leveling_handler(self, user, guild):
        guild_db = self.db[f"{guild.id}"]
        prev_lvl = guild_db.find_one({"_id": user.id})["level"]
        prev_exp = guild_db.find_one({"_id": user.id})["exp"]
        next_level = guild_db.find_one({"_id": user.id})["nextLevelExp"]

        exp = randint(1, 5)
        guild_db.update_one(
            {"_id": user.id},
            {"$inc": {
                "exp": exp
            }}
        )

        if (prev_exp + exp) > next_level:
            guild_db.update_one(
                {"_id": user.id},
                {"$inc": {
                    "level": 1
                }}
            )
            leftover = (prev_exp + exp) - next_level

            new_next_lvl = round(((next_level * 0.4 + next_level) / (prev_lvl + 1)) + next_level)
            guild_db.update_one(
                {"_id": user.id},
                {"$set": {
                    "nextLevelExp": new_next_lvl,
                    "exp": leftover
                }}
            )
            
            e = discord.Embed(description=f":tada: | **Congratulations, {user.mention}! You have reached __{prev_lvl + 1} level__!**", color=self.bot.color)
            return e


    @Cog.listener()
    async def on_command(self, ctx):
        self.bot.commands_used += 1

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        global_users = self.db["global"]
        global_user = {
            "_id"      :    message.author.id,
            "rep"      :    0,
            "desc"     :    None,
            "repTime"  :    datetime(2000, 1, 1, 1, 1, 1, 1),
            "pocket"   :    0,
            "bank"     :    0,
            "dailyTime":    datetime(2000, 1, 1, 1, 1, 1, 1),
        }

        try:
            global_users.insert_one(global_user)
        except pymongo.errors.DuplicateKeyError:
            pass

        ratelimit = self.get_ratelimit(message)
        if not ratelimit:
            # The user is not ratelimited so we can add exp
            e = await self.__leveling_handler(message.author, message.guild)
            
            try:
                await message.channel.send(embed = e)
            except discord.errors.HTTPException:
                pass

    @Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        guild = message.guild
        log_channel = self.bot.get_channel(self.db.settings.find_one({"_id": guild.id})["logChannel"])

        if log_channel:
            e = discord.Embed(title = ":wastebasket: | Message deleted", color = self.bot.color)
            e.add_field(name = "Sent by:", value = message.author.mention, inline=False)
            e.add_field(name = "In:", value = message.channel.mention, inline=False)
            e.add_field(name = "Content:", value = message.content, inline=False)

            await log_channel.send(embed = e)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        guild = before.guild
        log_channel = self.bot.get_channel(self.db.settings.find_one({"_id": guild.id})["logChannel"])

        if log_channel:
            e = discord.Embed(title = ":wastebasket: | Message edited", color = self.bot.color)
            e.add_field(name = "Sent by:", value = before.author.mention, inline=False)
            e.add_field(name = "In:", value = before.channel.mention, inline=False)
            e.add_field(name = "Before:", value = before.content, inline=False)
            e.add_field(name = "After:", value = after.content, inline=False)

            await log_channel.send(embed = e)

    @Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        guild = member.guild
        guild_db = self.db[str(guild.id)]
        welcome_channel = self.bot.get_channel(self.db.settings.find_one({"_id": guild.id})["welcomeChannel"])

        guild_member = {
            "_id"         :   member.id,
            "level"       :   1,
            "exp"         :   0,
            "nextLevelExp":   36,
            "warns"       :   []
        }
        guild_db.insert_one(guild_member)

        if welcome_channel:
            welcome_text = self.db.settings.find_one({"_id": guild.id})["welcomeMessage"]
            await welcome_channel.send(welcome_text.replace("?g", guild.name).replace("?n", member.display_name).replace("?@n", member.mention))

    @Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        guild_db = self.db[str(member.guild.id)]
        guild_db.delete_one({"_id": member.id})

    @Cog.listener()
    async def on_member_ban(self, guild, user):
        if user.bot:
            return

        log_channel = self.bot.get_channel(self.db.settings.find_one({"_id": guild.id})["logChannel"])
        guild_db = self.db[str(guild.id)]

        guild_db.delete_one({"_id": user.id})

        if log_channel:
            e = discord.Embed(title = ":hammer: | Operator banned", color = discord.Color.red())
            e.add_field(name = "Banned", value = user.mention, inline = False)
            e.set_thumbnail(url = user.avatar_url_as(format="png"))
            await log_channel.send(embed = e)

    @Cog.listener()
    async def on_member_unban(self, guild, user):
        if user.bot:
            return

        log_channel = self.bot.get_channel(self.db.settings.find_one({"_id": guild.id})["logChannel"])

        if log_channel:
            e = discord.Embed(title = ":hammer: | Operator unbanned", color = discord.Color.green())
            e.add_field(name = "Unbanned", value = user.mention, inline = False)
            e.set_thumbnail(url = user.avatar_url_as(format="png"))
            await log_channel.send(embed = e)

    @Cog.listener()
    async def on_guild_join(self, guild):
        self.db.create_collection(str(guild.id))

        guild_db = self.db[str(guild.id)]
        for member in guild.members:
            guild_member = {
            "_id"         :   member.id,
            "level"       :   1,
            "exp"         :   0,
            "nextLevelExp":   36,
            "warns"       :   []
            }
            guild_db.insert_one(guild_member)

        guild_settings = {
            "_id"           :   guild.id,
            "prefix"        :   "=",
            "logChannel"    :   None,
            "muteRoleID"    :   None,
            "welcomeChannel":   None,
            "welcomeMessage":   "Welcome to ?g, Dr. ?n",
            "warnAction"    :   False,
            "warnLimit"     :   3
        }
        self.db.settings.insert_one(guild_settings)

    @Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.db.drop_collection(str(guild.id))
        self.db.settings.delete_one({"_id": guild.id})


def setup(bot):
    bot.add_cog(EventHandler(bot))
