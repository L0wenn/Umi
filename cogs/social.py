import asyncio
import datetime
import operator
import random

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.db
        self.global_ = self.db["global"]
        self.farming = list()
         
    async def __calculate_place(self, user, guild):
        guild_db = self.db[str(guild.id)]
        userlist = list(guild_db.find())
        users = []
        
        for i in range(len(userlist)):
            try:
                uid = userlist[i]["_id"]
                level = userlist[i]["level"]
                users.append((uid, level))
            except:
                return "FTGPerr" #failed to get place

        sorted_list = sorted(users, key=operator.itemgetter(1), reverse=True)
 
        rank = 1
        for stats in sorted_list:
            if stats[0] == user.id:
                return rank
            rank += 1


    @commands.command(aliases=["xp", "lvl", "pf"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def profile(self, ctx, user: discord.Member = None):
        """Shows your profile. 
        Specify a user to get their profile instead"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        guild = self.db[str(ctx.guild.id)]

        user_guild = guild.find_one({"_id": user.id})
        user_global = self.global_.find_one({"_id": user.id})

        lvl = user_guild["level"]
        exp = user_guild["exp"]
        next_level = user_guild["nextLevelExp"]
        reps = user_global["rep"]
        place = await self.__calculate_place(user, ctx.guild)
        desc = user_global["desc"]

        e = discord.Embed(title=f"{user.display_name} Profile", description= f":up: | Level: **{lvl} ({exp}/{next_level})**\n" \
                                                                f":chart_with_upwards_trend: | Reputation: **{reps}**\n" \
                                                                f":medal: | Server Place: **{place}**", 
                        color=self.bot.color)
        e.add_field(name="Description", value=f"```{'Beep Boop, description!' if desc == None else desc}```")
        e.set_thumbnail(url=user.avatar_url_as(static_format='png'))
        await ctx.send(embed = e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, type = BucketType.user)
    async def rep(self, ctx, user: discord.Member):
        """Gives a reputation point to someone"""
        if user.bot:
            return
        if user == ctx.author:
            return

        last_rep = self.global_.find_one({"_id": ctx.author.id})["repTime"]
        dtnow = datetime.datetime.utcnow()
        diff = dtnow - last_rep
        left = datetime.timedelta(hours=23, minutes=59) - diff

        if diff.days == 0:
            s = left.total_seconds()
            h, m = s // 3600, (s % 3600) // 60
            e = discord.Embed(description = f":x: | You can reward a rep point again in `{int(h)}h` and `{int(m)}m`", color = discord.Color.red())
            return await ctx.send(embed = e)

        try:
            self.global_.update_one(
                {"_id": user.id},
                {"$inc": {
                    "rep": 1
                }}
            )
        except Exception:
            e = discord.Embed(title = ":x: | Failed to give a reputation point", color = discord.Color.red())
            return await ctx.send(embed = e)
        
        self.global_.update_one(
            {"_id": ctx.author.id},
            {"$set": {
                "repTime": datetime.datetime.utcnow()
            }}
        )

        e = discord.Embed(description = f"**:up: | {ctx.author.mention} has given {user.mention} a reputation point**", color = self.bot.color)
        return await ctx.send(embed = e)
    

    @commands.command(aliases=["desc"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def description(self, ctx, *, text: str = None):
        """Sets description for your profile
        Provide no text in order to reset your description
        """
        if text == None:
            self.global_.update_one(
                {"_id": ctx.author.id},
                {"$set": {
                    "desc": None
                }}
            )

            e = discord.Embed(title = ":page_facing_up: | Your description has been reset successfuly!", color = self.bot.color)
            return await ctx.send(embed=e)

        if len(text) > 125:
            e = discord.Embed(title = ":page_facing_up: | Your description is longer than 125 characters", color = discord.Color.red())
            return await ctx.send(embed=e)

        self.global_.update_one(
            {"_id": ctx.author.id},
            {"$set": {
                "desc": text
            }}
        )

        e = discord.Embed(title = ":page_facing_up: | Your description has been set!", color = self.bot.color)
        return await ctx.send(embed=e)


    @commands.command(aliases=["bal", "balance"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bank(self, ctx, user: discord.Member = None):
        """Shows your or someone else's balance"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        pocket = self.global_.find_one({"_id": user.id})["pocket"]
        bank = self.global_.find_one({"_id": user.id})["bank"]

        e = discord.Embed(title=f":atm: | {user.name} balance",
                    description=f":dollar: | Pocket: **`{pocket}`LMD**\n:bank: | Bank: **`{bank}`LMD**", color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def daily(self, ctx, user: discord.Member = None):
        """Take your dailies or give them someone. Also gives you a streak point which multiplies your daily"""
        if user == ctx.author:
            return
        if user == None:
            user = ctx.author
        if user.bot:
            return

        last_daily = self.global_.find_one({"_id": user.id})["dailyTime"]
        dtnow = datetime.datetime.utcnow()
        diff = dtnow - last_daily
        left = datetime.timedelta(hours=23, minutes=59) - diff

        if diff.days == 0:
            s = left.total_seconds()
            h, m = s // 3600, (s % 3600) // 60
            e = discord.Embed(title=":diamond_shape_with_a_dot_inside: | Daily",
                            description=f"You already claimed your daily today! You can claim again in `{int(h)}h` and `{int(m)}m`", color=self.bot.color)
            return await ctx.send(embed=e)
        else:
            streak = self.global_.find_one({"_id": user.id})["dailyStreak"]
            if diff.days > 1:
                streak = 0
                self.global_.update_one(
                    {"_id": user.id},
                    {"$set": {
                        "dailyStreak": 0
                    }}
                )

            daily = 75 * (streak + 1) // 5
            self.global_.update_one(
                {"_id": user.id},
                {"$inc": {
                    "pocket": daily,
                    "dailyStreak": 1
                }, 
                "$set": {
                    "dailyTime": datetime.datetime.utcnow()
                }}
            )

            if user != ctx.author:
                text = f"{ctx.author.mention} have given **{daily}LMD** to {user.mention}\n\n{ctx.author.mention} streak: **`{streak + 1}`**"
            else:
                text = f"You got **{daily}LMD** today! Your streak: **`{streak+1}`**"

            e = discord.Embed(title=":diamond_shape_with_a_dot_inside: | Daily", description=text, color=self.bot.color)
            return await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, type=BucketType.user)
    async def deposit(self, ctx, amount: int = None):
        """Sends your LMD to the local bank. Leave `amount` empty to deposit all your LMD at once"""
        if amount == None:
            amount = self.global_.find_one({"_id": ctx.author.id})["pocket"]

        self.global_.update_one(
            {"_id": ctx.author.id},
            {"$inc": {
                "pocket": -amount,
                "bank": amount
            }}
        )
        
        e = discord.Embed(title=":bank: | Deposit", description=f"**{amount}LMD** have been transfered to the bank", color=self.bot.color)
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, type=BucketType.user)
    async def withdraw(self, ctx, amount: int):
        """Gives you `<amount>` of LMD from the bank"""
        self.global_.update_one(
            {"_id": ctx.author.id},
            {"$inc": {
                "pocket": amount,
                "bank": -amount
            }}
        )
        
        e = discord.Embed(title=":bank: | Withdraw", description=f"**{amount}LMD** have been transfered to you from the bank", color=self.bot.color)
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def transfer(self, ctx, user: discord.Member, amount: int):
        """Transfer your LMD to someone"""
        if user.bot:
            return
        if user == ctx.author:
            return

        bal = self.global_.find_one({"_id": ctx.author.id})["pocket"]
        if bal < amount:
            e = discord.Embed(title=":atm: | Not enough LMD...", color=discord.Color.red())
            return await ctx.send(embed=e)

        code = random.randrange(1000, 9999)
        em = discord.Embed(title=":atm: | Waiting for confirmation...", color=discord.Color.orange())
        msg = await ctx.send(embed=em)
        e = discord.Embed(title=":atm: | Confirm your action", description=f"Your password is: **{code}**", color=self.bot.color)
        await ctx.author.send(embed=e)

        try:
            await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content == str(code), timeout=300)
        except asyncio.TimeoutError:
            e = discord.Embed(title=":atm: | Transfer", description=f"Timed out...", color=discord.Color.red())
            await ctx.send(embed=e)
        else:
            self.global_.update_one(
                {"_id": ctx.author.id},
                {"$inc": {
                    "pocket": -amount
                }}
            )
            self.global_.update_one(
                {"_id": user.id},
                {"$inc": {
                    "pocket": amount
                }}
            )

            e = discord.Embed(title=":atm: | Transfer", description=f"Successfuly transfered **{amount}LMD** to {user.mention}", color=self.bot.color)
            await msg.edit(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 30, type=BucketType.user)
    async def farm(self, ctx):
        """Farm LMD by "going" on operations"""
        if ctx.author.id in self.farming:
            e = discord.Embed(title=":crossed_swords: | You're already on operation", color=self.bot.color)
            return await ctx.send(embed=e)

        e = discord.Embed(title=f":crossed_swords: | Dr. {ctx.author.display_name} went on operation!", color = self.bot.color)
        msg = await ctx.send(embed=e)
        self.farming.append(ctx.author.id)

        await asyncio.sleep(300)
        lmd = random.randint(10, 150)
        self.global_.update_one(
            {"_id": ctx.author.id},
            {"$inc": {
                "pocket": lmd
            }}
        )
        self.farming.remove(ctx.author.id)

        await msg.delete()
        e = discord.Embed(title = f":crossed_swords: | {ctx.author.name} is back from the operation!",
                        description = f"Result of the operation: **{lmd}LMD**", color = self.bot.color)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Social(bot))
