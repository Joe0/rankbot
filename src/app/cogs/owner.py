import discord
from discord.ext import commands
import json
import random
from app.utils import embed

class OwnerCog():
    def __init__(self, bot):
        self.bot = bot
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *, cog: str):
        """Command which Loads a Module."""

        try:
            self.bot.load_extension(f'app.cogs.{cog}')
        except Exception as e:
            await ctx.send(embed=embed.error(description=f'**ERROR** - {type(e).__name__} - {e}'))
        else:
            await ctx.send(embed=embed.success(description='**SUCCESS**'))

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(f'app.cogs.{cog}')
        except Exception as e:
            await ctx.send(embed=embed.error(description=f'**ERROR** - {type(e).__name__} - {e}'))
        else:
            await ctx.send(embed=embed.success(description='**SUCCESS**'))

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(f'app.cogs.{cog}')
            self.bot.load_extension(f'app.cogs.{cog}')
        except Exception as e:
            await ctx.send(embed=embed.error(description=f'**ERROR** - {type(e).__name__} - {e}'))
        else:
            await ctx.send(embed=embed.success(description='**SUCCESS**'))

    @commands.group(name='add', hidden=True)
    @commands.is_owner()
    async def add_component(self, ctx):
        """Add a user, match, or deck to the bot."""

        if ctx.invoked_subcommand is None:
            await ctx.send(embed=embed.error(description=f'**ERROR** - Specify a component to add'))
            return

    @add_component.command(name='user', hidden=True)
    async def _add_user(self, ctx, *, user: discord.User):
        """Add a user to the database."""

        guild = ctx.message.guild
        if self.bot.db.add_member(user, guild):
            emsg = embed.msg(
                description = f"Registered **{user.name}** to the {guild.name} league"
            )
        else:
            emsg = embed.error(
                description = f"**{user.name}** is already registered"
            )
        await ctx.send(embed=emsg)

    def _load_deck_names(self, deckfile):
        with open(deckfile, "r") as infile:
            full_list = json.load(infile)
        decks = []
        for category in full_list:
            decks += [deck["name"] for deck in category["decks"]]
        return decks

    def _get_random_deck(self, deck_names):
        return decks_names[random.randint(0, len(deck_names)-1)]

    @add_component.command(name='match', hidden=True)
    async def _add_match(self, ctx):
        """Add a match to the database. Winner is the first player mentioned."""

        guild = ctx.message.guild
        users = ctx.message.mentions
        if len(users) != 4:
            await ctx.send(embed=embed.error(description=f'**ERROR** - Not enough players mentioned'))
            return
        winner = users[random.randint(0,3)]
        
        game_id = self.bot.db.add_match(ctx, winner, users)
        deck_names = self._load_deck_names("../config/decks.json")
        for user in users:
            rand_deck = self._get_random_deck(deck_names)
            self.bot.db.confirm_match_for_user(game_id, user.id, rand_deck, guild)
        delta = self.bot.db.check_match_status(game_id, guild)
        if delta:
            await ctx.send(embed=embed.success(description=f'**SUCCESS** - Added {game_id}'))

    def _load_decks(self):
        with open("../config/decks.json", "r") as infile:
            decks = json.load(infile)
        decks_added = 0
        for category in decks:
            for deck in category["decks"]:
                decks_added += self.bot.db.add_deck(
                    category["colors"], 
                    category["color_name"],
                    deck["name"],
                    deck["nicknames"]
                )
        return decks_added


    @commands.command(name="reload-decks")
    @commands.is_owner()
    async def reload_decks(self, ctx):
        decks_added = self._load_decks()
        if not decks_added:
            await ctx.send(embed=embed.info(
                description=f"Nothing new to import"))
        else:
            await ctx.send(embed=embed.success(
                description=f"**SUCCESS** - {decks_added} new decks imported"))
        


def setup(bot):
    bot.add_cog(OwnerCog(bot))
