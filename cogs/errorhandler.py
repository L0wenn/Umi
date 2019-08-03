import discord
from discord.ext import commands
import sys
import traceback


class ErrorHander(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    async def __build_error_embed(self, title, description=discord.Embed.Empty, color=discord.Color.red()):
        e = discord.Embed(title=title, description=description, color=color)
        return e


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return
        
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f":x: | **{ctx.command} can not be used in Private Messages**")
            except:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            e = discord.Embed(title=f":clock1: | Chill! You can use the command again after {round(error.retry_after)}s", color=discord.Color.orange())
            return await ctx.send(embed=e)

        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perms.replace("_", ' ').replace("guild", "server").title() for perms in error.missing_perms]
            if len(missing) > 2:
                fmt = f"{', '.join(missing[:-1])}, and {missing[-1]}"
            else:
                fmt = f" and ".join(missing)

            e = await self.__build_error_embed(":x: | Bot Missing Permissions", f"I am missing some permissions to run this command: ```{fmt}```")
            return await ctx.send(embed=e)

        elif isinstance(error, commands.DisabledCommand):
            e = await self.__build_error_embed(":x: | This command is dissabled")
            return await ctx.send(embed=e)

        elif isinstance(error, commands.UserInputError):
            pass

        elif isinstance(error, commands.CheckFailure):
            e = await self.__build_error_embed(":x: | You don't have permissions to use this command")
            await ctx.send(embed=e)

        elif isinstance(error, commands.MissingPermissions):
            missing = [perms.replace("_", ' ').replace("guild", "server").title() for perms in error.missing_perms]
            if len(missing) > 2:
                fmt = f"{', '.join(missing[:-1])}, and {missing[-1]}"
            else:
                fmt = f" and ".join(missing)

            e = await self.__build_error_embed(":x: | Bot Missing Permissions", f"You need permissions to run this command: ```{fmt}```")
            return await ctx.send(embed=e)


        #ignore all other exception types, but print them in stderr
        print(f"Ignoring exception in command {ctx.command}:", file=sys.stderr)

        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHander(bot))