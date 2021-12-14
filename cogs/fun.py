import random
import re

import discord
import nekos
from discord.ext import commands
from discord.ext.commands import BucketType

from cogs.utils.helpers import get_image, get_json


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#start of nekobot functions: https://github.com/hibikidesu/NekoBot
    # TODO: Discord doesn't want to attach a pic to embeds for some reason?
    def __nekobot_embed(self, data, key="message"):
        e = discord.Embed(color=self.bot.color)
        e.set_image(url=data[key])
        e.set_footer(text="Powered by: https://nekobot.xyz/")
        return e

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def blurpify(self, ctx, user:discord.Member=None):
        """Blurpify something!"""
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=blurpify&image={img}")
        await ctx.send(embed=self.__nekobot_embed(res))


    @commands.command(aliases=["phc", "ph"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def phcomment(self, ctx, *, comment: str):
        """PronHub comment image :lenny:"""
        await ctx.trigger_typing()
        res = await get_json("https://nekobot.xyz/api/imagegen?type=phcomment"
                                    f"&image={ctx.author.avatar_url_as(format='png')}"
                                    f"&text={comment}&username={ctx.author.name}")
        if not res["success"]:
            e = discord.Embed(title=":x: | Failed to successfully get the image...", color=discord.Color.red())
            return await ctx.send(embed=e)
        await ctx.send(embed=self.__nekobot_embed(res))


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def tweet(self, ctx, username: str, *, text: str):
        """Make a tweet as someone!"""
        await ctx.trigger_typing()
        res = await get_json("https://nekobot.xyz/api/imagegen?type=tweet"
                                    f"&username={username}&text={text}")
        await ctx.send(embed=self.__nekobot_embed(res))


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def threats(self, ctx, user:discord.Member):
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=threats&url={img}")
        await ctx.send(embed=self.__nekobot_embed(res))


    @commands.command(aliases=["bp", "pillow"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def bodypillow(self, ctx, user:discord.Member):
        """Bodypillow someone uwu"""
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=bodypillow&url={img}")
        await ctx.send(embed=self.__nekobot_embed(res))

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def baguette(self, ctx, user:discord.Member):
        """:^)"""
        await ctx.trigger_typing()
        img = user.avatar_url_as(format="png")
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=baguette&url={img}")
        await ctx.send(embed=self.__nekobot_embed(res))

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def deepfry(self, ctx, user:discord.Member=None):
        """Deepfry a user"""
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=deepfry&image={img}")
        await ctx.send(embed=self.__nekobot_embed(res))
    
    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)   
    async def clyde(self, ctx, *, text: str):
        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}")
        await ctx.send(embed=self.__nekobot_embed(res))

    #jeez, kill me pls
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user) 
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Ship people OwO ~~You also can ship yourself with yourself~~"""
        if user2 == None:
            user2 = ctx.author

        await ctx.trigger_typing()
        if user1.avatar:
            user1_url = f"https://cdn.discordapp.com/avatars/{user1.id}/{user1.avatar}.png"
        else:
            user1_url = "https://cdn.discordapp.com/embed/avatars/1.png"
        if user2.avatar:
            user2_url = f"https://cdn.discordapp.com/avatars/{user2.id}/{user2.avatar}.png"
        else:
            user2_url = "https://cdn.discordapp.com/embed/avatars/1.png"

        self_lengh = len(user1.name)
        first_lengh = round(self_lengh / 2)
        first_half = user1.name[0:first_lengh]
        usr_lengh = len(user2.name)
        second_lengh = round(usr_lengh / 2)
        second_half = user2.name[second_lengh:]
        final_name = first_half + second_half

        score = random.randint(0, 100)
        if user1.name == user2.name:
            score = 100
        filled_progbar = round(score / 100 * 10)
        counter_ = "█" * filled_progbar + " " * (10 - filled_progbar)
        
        if score >= 0 and score <= 25:
            color = discord.Color.red()
        if score > 25 and score <= 75:
            color = discord.Color.orange()
        if score > 75 and score <= 100:
            color = discord.Color.green()

        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=ship&user1={user1_url}&user2={user2_url}")
        e = discord.Embed(title=f"{user1.name} :heart: {user2.name}", 
                        description="**Love %**\n" \
                                    f"`{counter_}` **{score}%**\n\n{'Selfcest is the bestcest!' if user1 == user2 else final_name}",
                        color=color)
        e.set_image(url=res["message"])
        await ctx.send(embed=e)


    @commands.command(aliases=["FBI", "jail"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def lolice(self, ctx):
        """*KNOCK KNOCK KNOCK* FBI OPEN UP!"""
        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=lolice&url={ctx.author.avatar_url_as(format='png')}")
        await ctx.send(embed=self.__nekobot_embed(res))

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def trash(self, ctx, user:discord.Member):
        """trash smh"""
        await ctx.trigger_typing()
        url = user.avatar_url_as(format="jpg")
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=trash&url={url}")
        await ctx.send(embed=self.__nekobot_embed(res))

    
    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def awooify(self, ctx, user: discord.Member = None):
        """*Awoo noises intensifies*"""
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=awooify&url={img}")
        await ctx.send(embed=self.__nekobot_embed(res))

    
    @commands.command(aliases=["cmm"])
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def changemymind(self, ctx, *, text: str):
        """Do it. You won't"""
        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=changemymind&text={text}")
        await ctx.send(embed=self.__nekobot_embed(res))


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, type=BucketType.user)
    async def magik(self, ctx, user: discord.Member = None):
        """Magikify a user/picture"""
        img = await get_image(self.bot, ctx, user)
        if not isinstance(img, str):
            return img

        await ctx.trigger_typing()
        res = await get_json(f"https://nekobot.xyz/api/imagegen?type=magik&image={img}")
        await ctx.send(embed=self.__nekobot_embed(res))
#end of nekobot functions: https://github.com/hibikidesu/NekoBot


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def roll(self, ctx, dice: str):
        """Roll the dice in NdN format
        
        Example: **1d20** (1 dice with 20 faces)
        """
        faces = []
        r = re.compile(".*d.*")
        if not r.match(dice):
            e = discord.Embed(title=":x: | Dice should be in NdN format", color=discord.Color.red())
            return await ctx.send(embed=e)
        
        dices = list(map(int, dice.split("d")))
        total = dices[0] * dices[1]
        for i in range(dices[0]):
            faces.append(random.randrange(1, dices[1]))
            
        got = sum(faces)
        pers = got / total
        if pers <= 0.25:
            color = discord.Color.dark_red()
        elif pers > 0.25 and pers <= 0.50:
            color = discord.Color.red()
        elif pers > 0.50 and pers <= 0.75:
            color = discord.Color.orange()
        else:
            color = discord.Color.green()
            
        e = discord.Embed(title=f":game_die: | {ctx.author.name} rolled the dice!", color=color)
        e.add_field(name="Results", value=f"**Dice landed on:** {' '.join(list(map(str, faces)))}\n**Total:** {got}")
        await ctx.send(embed=e)
    

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def meme(self, ctx):
        """Sends you a random meme from Reddit"""
        await ctx.trigger_typing()
        res = await get_json("https://www.reddit.com/r/memes.json")

        post = random.choice(res["data"]["children"])
        meme = post["data"]

        e = discord.Embed(color=0xFF4500)
        e.set_author(name=f"{meme['title']}", url=f"https://www.reddit.com{meme['permalink']}")
        e.set_image(url=meme["url"])

        await ctx.send(embed=e)

    
    @commands.command(aliases=["coin"])
    @commands.guild_only()
    @commands.cooldown(1, 3, type=BucketType.user)
    async def flipcoin(self, ctx):
        """Flips a coin for you!"""
        coin = random.randint(0, 1)
        img = discord.File("images/tails.png" if coin == 0 else "images/heads.png")
        filename = "attachment://tails.png" if coin == 0 else "attachment://heads.png"
        e = discord.Embed(title="TAILS!!" if coin == 0 else "HEADS!!", color=self.bot.color)
        e.set_image(url=filename)
        await ctx.send(embed=e, file=img)


    @commands.command(name="8ball")
    @commands.guild_only()
    @commands.cooldown(1, 6, type=BucketType.user)
    async def eightball(self, ctx):
        """Ask a question to the ball and it'll show you the answer"""
        ball = nekos.eightball()
        e = discord.Embed(title = ball.__getattr__("text"), color = 0x000000)
        e.set_image(url = ball.__getattr__("image"))
        await ctx.send(embed=e)


    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 6, type=BucketType.user)
    async def fact(self, ctx):
        """Sends you a random fact"""
        await ctx.trigger_typing()
        e = discord.Embed(title=":bookmark: | Random Fact!", description=nekos.fact(), color=self.bot.color)
        await ctx.send(embed=e)

    
    @commands.command(aliases=["owo", "weebify"])
    @commands.guild_only()
    @commands.cooldown(1, 10, type=BucketType.user)
    async def owoify(self, ctx, *, text: str):
        """OWOifies your text. Cuuuuute"""
        await ctx.message.delete()
        e = discord.Embed(title="OwO", description=nekos.owoify(text), color=self.bot.color)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Fun(bot))
