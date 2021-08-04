import discord
import itertools
from discord.ext import commands

class BotHelp(commands.MinimalHelpCommand):

    def get_opening_note(self):
        return "Down below listed all commands I know.\n" \
            "If you need further help on something, please, join our [Support Server](https://discordpy.readthedocs.io/en/latest/)"

    def get_ending_note(self):
        command_name = self.invoked_with
        return "Use {0}{1} [command] for more info on a command.\n" \
               "You can also use {0}{1} [category] for more info on a category.".format(self.clean_prefix, command_name)

    def add_bot_commands_formatting(self, commands, heading, embed):
        if commands:
            joined = "`"+"`\u2002`".join(c.name for c in commands)+"`"
            embed.add_field(name=heading, value=joined, inline=False)

    def add_subcommand_formatting(self, command):
        fmt = '{0}{1} : {2}\n' if command.short_doc else '{0}{1}\n'
        return fmt.format(self.clean_prefix, command.qualified_name, command.short_doc) 

    async def send_embed(self, embed):
        destination = self.get_destination()
        await destination.send(embed=embed)
        
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        e = discord.Embed(title=":abcd: | Help", description=self.get_opening_note(), color=0x98ff98)
        e.set_thumbnail(url=bot.user.avatar_url_as(format="png"))
        e.set_footer(text=self.get_ending_note())

        def get_category(command):
            cog = command.cog
            return cog.qualified_name

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        to_iterate = itertools.groupby(filtered, key=get_category)

        for category, commands in to_iterate:
            commands = sorted(commands, key=lambda c: c.name) if self.sort_commands else list(commands)
            self.add_bot_commands_formatting(commands, category, e)

        await self.send_embed(e)

    async def send_cog_help(self, cog):
        cog_help = str()
        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        if filtered:
            for command in filtered:
                cog_help += self.add_subcommand_formatting(command)

        destination = self.get_destination()
        await destination.send(f"```apache\n[{cog.qualified_name} Commands]\n\n{cog_help}```")

    async def send_command_help(self, command):
        signature = self.get_command_signature(command)
        fmt_aliases = "`" + "`\u2002`".join(command.aliases) + "`"

        e = discord.Embed(title=f":abcd: | Help: {signature}", description=f"{command.help}\n\n"\
        f"Aliases: {fmt_aliases}", color=0x98ff98)
        e.set_footer(text="<> - Nessesary, [] - Optional")

        await self.send_embed(e)
