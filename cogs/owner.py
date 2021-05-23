import ast
import traceback

import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def __create_embed(self, title, description, color, emote):
        e = discord.Embed(title=f"{emote} | {title}", description=description, color=color)
        return e

    
    async def __send_to_log_channel(self, title, description, color):
        log_channel_id = 627815860181925895
        channel = self.bot.get_channel(log_channel_id)

        e = discord.Embed(title = title, description = description, color = color)
        await channel.send(embed = e)


    def insert_returns(self, body):
    # insert return stmt if the last expression is a expression statement
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the orelse
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)
    

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            self.bot.load_extension("cogs." + cog)
            e = await self.__create_embed("Next cog was loaded", f"```{cog}```", discord.Color.green(), ":white_check_mark:")
            await ctx.send(embed=e)
        except Exception:
            await ctx.send(f"`Error!` ```{traceback.format_exc()}```")  


    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, cog):
        try:
            self.bot.unload_extension("cogs." + cog)
            e = await self.__create_embed("Next cog was unloaded", f"```{cog}```", discord.Color.red(), ":no_entry:")
            await ctx.send(embed=e)
        except Exception:
            await ctx.send(f"`Error!` ```{traceback.format_exc()}```")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, cog):
        try:
            self.bot.reload_extension("cogs." + cog)
            e = await self.__create_embed("Next cog was reloaded", f"```{cog}```", discord.Color.orange(), ":repeat:")
            await ctx.send(embed=e)
        except Exception:
            return await ctx.send(f"`Error!` ```{traceback.format_exc()}```")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def py(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline seperated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
        - `bot`: the bot instance
        - `discord`: the discord module
        - `commands`: the discord.ext.commands module
        - `ctx`: the invokation context
        - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invokation will cause the bot to send the text '9'
        to the channel of invokation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        fn_name = "_eval_expr"

        cmd = cmd.strip("` ")

        # add a layer of indentation
        cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

        # wrap in async def body
        body = f"async def {fn_name}():\n{cmd}"

        parsed = ast.parse(body)
        body = parsed.body[0].body

        self.insert_returns(body)

        env = {
            'bot': ctx.bot,
            'discord': discord,
            'commands': commands,
            'ctx': ctx,
            '__import__': __import__
        }
        exec(compile(parsed, filename="<ast>", mode="exec"), env)

        try:
            result = (await eval(f"{fn_name}()", env))
        except Exception as e:
            await ctx.send(f"`Error:` ```python\n{e}```")
        
        try:
            await ctx.send(result)
        except:
            pass
        
    
def setup(bot):
    bot.add_cog(Owner(bot))
