from discord.ext import commands
import discord

from util.code import format_exception

IGNORED_ERRORS = (commands.CommandNotFound, commands.NotOwner)

BAD_ARG_ERRORS = (
    commands.BadArgument,
    commands.errors.UnexpectedQuoteError,
    commands.errors.ExpectedClosingQuoteError,
    commands.errors.BadUnionArgument,
)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.d = bot.d

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("My Discord bot is running and ready!")

    async def handle_cooldown(self, ctx, remaining: float) -> None:
        seconds = round(remaining, 2)

        if seconds <= 0.05:
            await ctx.reinvoke()
            return

        hours = int(seconds / 3600)
        minutes = int(seconds / 60) % 60
        time_nice = ""

        seconds -= round((hours * 60 * 60) + (minutes * 60), 2)

        if hours == 1:
            time_nice += f"{hours} hour, "
        elif hours > 0:
            time_nice += f"{hours} hours, "

        if minutes == 1:
            time_nice += f"{minutes} minute, "
        elif minutes > 0:
            time_nice += f"{minutes} minutes, "

        if seconds == 1:
            time_nice += f"{round(seconds, 2)} second"
        elif seconds > 0:
            time_nice += f"{round(seconds, 2)} seconds"

        await self.bot.reply_embed(
            ctx, f"Hold on! You need to wait {time_nice} before using that command again.", ignore_exceptions=True
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, e: Exception):
        if isinstance(e, commands.CommandOnCooldown):
            await self.handle_cooldown(ctx, e.retry_after)
        elif isinstance(e, commands.NoPrivateMessage):
            await self.bot.reply_embed(ctx, "You can't use that command here.", ignore_exceptions=True)
        elif isinstance(e, commands.MissingPermissions):
            await self.bot.reply_embed(ctx, "You don't have the permissions to use that command.", ignore_exceptions=True)
        elif isinstance(e, (commands.BotMissingPermissions, discord.errors.Forbidden)):
            await self.bot.reply_embed(ctx, "I don't have the permissions to do that.", ignore_exceptions=True)
        elif getattr(e, "original", None) is not None and isinstance(e.original, discord.errors.Forbidden):
            await self.bot.reply_embed(ctx, "I don't have the permissions to do that.", ignore_exceptions=True)
        elif isinstance(e, commands.MaxConcurrencyReached):
            await self.bot.reply_embed(ctx, "Hold on, you're already using that command.", ignore_exceptions=True)
        elif isinstance(e, commands.MissingRequiredArgument):
            await self.bot.reply_embed(
                ctx, "Looks like you typed something wrong, you may be missing something.", ignore_exceptions=True
            )
        elif isinstance(e, BAD_ARG_ERRORS):
            await self.bot.reply_embed(ctx, "Looks like you typed something wrong, please try again.", ignore_exceptions=True)
        elif isinstance(e, IGNORED_ERRORS) or isinstance(getattr(e, "original", None), IGNORED_ERRORS):
            return
        else:
            await self.bot.wait_until_ready()
            await self.bot.reply_embed(ctx, "Something went wrong...", ignore_exceptions=True)

            debug_info = (
                f"```\n{ctx.author} {ctx.author.id}: {ctx.message.content}"[:200]
                + "```"
                + f"```py\n{format_exception(e)}"[: 2000 - 206]
                + "```"
            )

            await self.bot.get_channel(self.d.error_channel_id).send(debug_info)

def setup(bot):
    bot.add_cog(Events(bot))
