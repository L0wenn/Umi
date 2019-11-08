import asyncio
import datetime
import traceback  # for debugging purposes
import random 

import discord
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils import database as db


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.working = list()

    
    async def check_bank_account(self, userID):
        try:
            account = await db.get("id", "bank", f"id = {userID}")
            if account:
                return True
        except:
            return False

    def noBank_error_message_yourself(self):
        e = discord.Embed(description = "You don't have a bank account yet. To create one use `create` command", color = discord.Color.red())
        return e

    def noBank_error_message_someone(self, user):
        return f"{user.mention} doesn't have a bank account yet..."


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def create(self, ctx):
        """Creates a bank account"""
        if await self.check_bank_account(ctx.author.id):
            e = discord.Embed(title=":atm: | Account already exists!", color=self.bot.color)
            await ctx.send(embed=e)
        else:
            await db.insert("bank", f'({ctx.author.id}, 0, 0, datetime("2000-01-01 00:00:00"), 0)')
            e = discord.Embed(title=":atm: | Account Created", color=self.bot.color)
            await ctx.send(embed=e)

    
    @commands.command(aliases=["bal", "balance"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bank(self, ctx, user: discord.Member = None):
        """Shows your or someones balance"""
        if user == None:
            user = ctx.author
        if user.bot:
            return

        try:
            pocket = await db.get("pocket", "bank", f"id = {user.id}")
            bank = await db.get("bank", "bank", f"id = {user.id}")

            e = discord.Embed(title=f":atm: | {user.name} balance",
                        description=f":dollar: | Pocket: **`{pocket}`$**\n:bank: | Bank: **`{bank}`$**", color=self.bot.color)
            await ctx.send(embed=e)
        except TypeError:
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)


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
        if not await self.check_bank_account(user.id):
            return
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)

        date = await db.get("lastDaily", "bank", f"id = {user.id}")
        last_daily = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        dtnow = datetime.datetime.now()
        diff = dtnow - last_daily
        left = datetime.timedelta(hours=23, minutes=59) - diff

        if diff.days == 0:
            s = left.total_seconds()
            h, m = s // 3600, (s % 3600) // 60
            e = discord.Embed(title=":diamond_shape_with_a_dot_inside: | Daily",
                            description=f"You already claimed your daily today! You can claim again in `{int(h)}h` and `{int(m)}m`", color=self.bot.color)
            return await ctx.send(embed=e)
        else:
            streak = await db.get("dailyStreak", "bank", f"id = {user.id}")
            if diff.days > 1:
                streak = 0
                await db.update("bank", f"dailyStreak = 0", f"id = {user.id}")

            daily = 75 * (streak + 1) // 5
            await db.update("bank", f"pocket = pocket + {daily}", f"id = {user.id}")
            await db.update("bank", f"dailyStreak = dailyStreak + 1", f"id = {ctx.author.id}")
            await db.update("bank", f'lastDaily = datetime("now", "localtime")', f"id = {ctx.author.id}")

            if user != ctx.author:
                text = f"{ctx.author.mention} have given **{daily}$** to {user.mention}\n\n{ctx.author.mention} streak: **`{streak+1}`**"
            else:
                text = f"You got **{daily}$** today! Your streak: **`{streak+1}`**"

            e = discord.Embed(title=":diamond_shape_with_a_dot_inside: | Daily", description=text, color=self.bot.color)
            return await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, type=BucketType.user)
    async def deposit(self, ctx, amount: int = None):
        """Sends your money to the local bank. Leave `amount` empty to deposit all your money at once"""
        if amount == None:
            pocket = await db.get("pocket", "bank", f"id = {ctx.author.id}")
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)

        await db.update("bank", f"pocket = pocket - {pocket if amount == None else amount}", f"id = {ctx.author.id}")
        await db.update("bank", f"bank = bank + {pocket if amount == None else amount}", f"id = {ctx.author.id}")
        
        e = discord.Embed(title=":bank: | Deposit", description=f"**{pocket if amount == None else amount}$** were transfered to the bank", color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 7, type=BucketType.user)
    async def withdraw(self, ctx, amount: int):
        """Gives you `<amount>` of money from the bank"""
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)

        await db.update("bank", f"pocket = pocket + {amount}", f"id = {ctx.author.id}")
        await db.update("bank", f"bank = bank - {amount}", f"id = {ctx.author.id}")
        
        e = discord.Embed(title=":bank: | Withdraw", description=f"**{amount}$** were transfered to you from the bank", color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def transfer(self, ctx, user: discord.Member, amount: int):
        """Transfer your money to someone"""
        if user.bot:
            return
        if user == ctx.author:
            return
        if not await self.check_bank_account(user.id):
            e = discord.Embed(title=":atm: | Transfer", description=self.noBank_error_message_someone(user), color=discord.Color.red())
            return await ctx.send(embed=e)

        bal = await db.get("pocket", "bank", f"id = {ctx.author.id}")
        if bal < amount:
            e = discord.Embed(title=":atm: | Not enough money...", color=discord.Color.red())
            return await ctx.send(embed=e)

        code = random.randrange(1000, 9999)
        em = discord.Embed(title=":atm: | Waiting for confirm...", color=discord.Color.orange())
        msg = await ctx.send(embed=em)
        e = discord.Embed(title=":atm: | Confirm your action", description=f"Your password is: **{code}**", color=self.bot.color)
        await ctx.author.send(embed=e)

        try:
            await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content == str(code), timeout=300)
        except asyncio.TimeoutError:
            e = discord.Embed(title=":atm: | Transfer", description=f"Timed out...", color=discord.Color.red())
            await ctx.send(embed=e)
        else:
            await db.update("bank", f"pocket = pocket - {amount}", f"id = {ctx.author.id}")
            await db.update("bank", f"pocket = pocket + {amount}", f"id = {user.id}")

            e = discord.Embed(title=":atm: | Transfer", description=f"Successfuly transfered **{amount}$** to {user.mention}", color=self.bot.color)
            await msg.edit(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 30, type=BucketType.user)
    async def work(self, ctx):
        """Go to work and get paid for this!"""
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)
        if ctx.author.id in self.working:
            e = discord.Embed(title=":convenience_store: | You're already at work", color=self.bot.color)
            return await ctx.send(embed=e)

        e = discord.Embed(title=f":convenience_store: | {ctx.author.name} went to work!", color = self.bot.color)
        msg = await ctx.send(embed=e)
        self.working.append(ctx.author.id)

        await asyncio.sleep(300)
        salary = random.randint(10, 150)
        await db.update("bank", f"pocket = pocket + {salary}", f"id = {ctx.author.id}")
        self.working.remove(ctx.author.id)

        await msg.delete()
        e = discord.Embed(title = f":convenience_store: | {ctx.author.name} is back from work!",
                        description = f"You've been working good today and got **{salary}$**!", color = self.bot.color)
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 60, type=BucketType.user)
    async def rob(self, ctx, user: discord.Member):
        """Get free money or get caught. How lucky are you?"""
        if user == ctx.author:
            return
        if user.bot:
            return
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)

        fate = random.randint(0, 2)
        if fate < 2: #Luck
            try:
                victim = await db.get("pocket", "bank", f"id = {user.id}")
            except:
                e = discord.Embed(title = f":thinking: | {ctx.author.name}, your victim doesn't even have a bank account yet...", 
                                color=discord.Color.red())
                return await ctx.send(embed=e)
            
            robbed = round(victim * (random.randint(0, 100) / 100))
            await db.update("bank", f"pocket = pocket + {robbed}", f"id = {ctx.author.id}")
            await db.update("bank", f"pocket = pocket - {robbed}", f"id = {user.id}")

            e = discord.Embed(title = ":moneybag: | Robbery!!!",
                            description = f"{user.mention} got robbed by {ctx.author.mention} **({robbed}$)**",
                            color = self.bot.color)
            await ctx.send(embed=e)
        else: #Got caught
            loser = await db.get("pocket", "bank", f"id = {ctx.author.id}")
            fine = round(loser * (random.randint(0, 25) / 100))
            await db.update("bank", f"pocket = pocket - {fine}", f"id = {ctx.author.id}")

            e = discord.Embed(title = ":moneybag: | Robbery!!!",
                            description = f"{ctx.author.mention} got caught on robbery and was fined for **{fine}$**",
                            color = self.bot.color)
            await ctx.send(embed=e)

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 120, type=BucketType.user)
    async def slut(self, ctx):
        """Satisfy a customer and get paid for this..."""
        if not await self.check_bank_account(ctx.author.id):
            e = self.noBank_error_message_yourself             
            return await ctx.send(embed=e)

        mood = random.randint(0, 1) #no chances like for robbery
        if mood == 0:
            payment = random.randint(500, 2000)
            restock = round(payment * (random.randint(0, 5) / 100))
            total = payment - restock

            await db.update("bank", f"pocket = pocket + {total}", f"id = {ctx.author.id}")
            e = discord.Embed(title=":lollipop: | Slut...",
                            description = f"You've worked well on pleasuring your customer and got paid **{payment}$**, " \
                                            f"but you spent **{restock}$** to restock something.\n\nIn total you got: **{total}$**",
                            color = 0xDEADBF)
            await ctx.send(embed=e)
        else:
            payment = random.randint(50, 300)
            restock = round(payment * (random.randint(0, 20) / 100))
            total = payment - restock

            await db.update("bank", f"pocket = pocket + {total}", f"id = {ctx.author.id}")
            e = discord.Embed(title=":lollipop: | Slut...",
                            description = f"Your customer wasn't satisfied by you and paid only **{payment}$**, " \
                                            f"you also spent **{restock}$** to restock something.\n\nIn total you got: **{total}$**",
                            color = 0xDEADBF)
            await ctx.send(embed=e)

        
def setup(bot):
    bot.add_cog(Currency(bot))
