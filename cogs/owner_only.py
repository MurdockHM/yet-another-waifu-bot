import discord
from discord.ext.commands import Cog, Context, NotOwner, command
from my_bot import MyBot
from player import players
from bot_config import bot_config
from waifu_manager import waifu_manager
from timers import timers
import aiohttp


class OwnerOnly(Cog, name="Owner Commands"):
    
    def __init__(self, bot: MyBot):
        self.bot = bot
        self.last_game = discord.Game("")
        self.last_status = discord.Status.online
    
    async def cog_command_error(self, ctx: Context, error):
        if isinstance(error, NotOwner):
            await ctx.send("You're not my dad.")
        raise error
    
    async def cog_check(self, ctx: Context):
        if await self.bot.is_owner(ctx.message.author):
            return True
        raise NotOwner

    @command()
    async def dismiss(self, ctx: Context):
        await ctx.message.add_reaction('👌')
        await self.bot.logout()
    
    @command()
    async def change_avatar(self, ctx: Context, url: str):
        with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                avatar_b = await resp.read()
                await self.bot.edit_profile(avatar=avatar_b)
    
    @command()
    async def add_players(self, ctx: Context):
        guild = ctx.message.guild
        for member in guild.members:
            if not member.bot:
                players.add_player(member.id, member.name)
        await ctx.send("Updated player database")
    
    @command()
    async def say(self, ctx: Context, channel_id: int, *args: str):
        channel = self.bot.get_channel(channel_id)
        msg = ' '.join(args)
        if ctx.message.author.id == 178887072864665600:
            await channel.send(msg)
    
    @command()
    async def set_game(self, ctx: Context, *args):
        game_name = ' '.join(args)
        game = discord.Game(game_name)
        self.last_game = game
        await self.bot.change_presence(activity=game, status=self.last_status)
    
    @command()
    async def set_status(self, ctx: Context, status: str):
        states = {
            'online': discord.Status.online,
            'offline': discord.Status.offline,
            'idle': discord.Status.idle,
            'dnd': discord.Status.dnd
        }
        status = states.get(status, None)
        if status is None:
            await ctx.send("Uh, are you sure you're not going senile?")
            return
        self.last_status = status
        await self.bot.change_presence(activity=self.last_game, status=status)
    
    @command()
    async def cheat_spawn(self, ctx: Context, waifu_id: int):
        waifu_commands = self.bot.get_cog("Waifu Commands")
        response = await waifu_commands.get_waifu_by_id(waifu_id)
        pictures = await waifu_commands.get_mal_waifu_pics(waifu_id)
        waifu_manager.prepare_waifu_spawn(response, pictures['pictures'])
        embed = waifu_manager.spawn_waifu()
        message = await ctx.send(embed=embed)
        waifu_manager.set_claim_message(message)
        timers.set_waifu_claim_timer()


def setup(bot: MyBot):
    c = OwnerOnly(bot)
    bot.add_cog(c)

