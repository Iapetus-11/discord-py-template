from pretty_help import PrettyHelp
from discord.ext import commands
import classyjson as cj
import discord

from util.setup import setup_logging

with open("config.json", "r") as config_file:
    CONFIG = cj.load(config_file)
    CONFIG.embed_color = discord.Color.from_rgb(*CONFIG.embed_color)


class MyDiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=discord.Intents.all(),
            help_command=PrettyHelp(color=CONFIG.embed_color),
        )

        self.logger = setup_logging()
        self.d = CONFIG

        self.cogs_list = [
            "cogs.core.events",
            "cogs.commands.debug",
        ]

    async def start(self, *args, **kwargs):
        for cog in self.cogs_list:
            self.load_extension(cog)

        await super().start(*args, **kwargs)

    async def get_prefix(self, ctx):
        return CONFIG.default_prefix

    async def send_embed(self, location, message: str, *, ignore_exceptions: bool = False) -> None:
        try:
            await location.send(embed=discord.Embed(color=self.d.cc, description=message))
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            if not ignore_exceptions:
                raise

    async def reply_embed(self, location, message: str, ping: bool = False, *, ignore_exceptions: bool = False) -> None:
        try:
            await location.reply(embed=discord.Embed(color=self.d.cc, description=message), mention_author=ping)
        except discord.errors.HTTPException:
            await self.send_embed(location, message, ignore_exceptions=ignore_exceptions)
        except discord.errors.Forbidden:
            if not ignore_exceptions:
                raise


if __name__ == "__main__":
    MyDiscordBot().run(CONFIG.discord_token)
