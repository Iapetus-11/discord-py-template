from discord.ext import commands

from util.code import format_exception, execute_code


class Debug(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload", aliases=["reloadcog"])
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        try:
            self.bot.reload_extension(f"cogs.{cog}")
        except Exception as e:
            await ctx.send(f"Error while reloading `cogs.{cog}`: ```py\n{format_exception(e)}```")

    @commands.command(name="eval")
    @commands.is_owner()
    async def eval_stuff_local(self, ctx, *, stuff: str):
        if stuff.startswith("```"):
            stuff = stuff.lstrip(" `py\n ").rstrip(" `\n ")

        try:
            result = await execute_code(stuff, {**globals(), **locals(), "bot": self.bot})
            await ctx.reply(f"```{str(result).replace('```', '｀｀｀')}```")
        except Exception as e:
            await ctx.reply(f"```py\n{format_exception(e)[:2000-9]}```")

def setup(bot):
    bot.add_cog(Debug(bot))
