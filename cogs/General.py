import discord
import discord.errors
from discord.ext import commands
from typing import Optional

class General(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.green = 0x3ecf43
        self.red = 0xe61212

    def cog_cleaner(self, cog: str):
        return ''.join(filter(str.isalpha, cog)) 

    @commands.command(aliases = ['l'],
                      help = "**Owner only**", 
                      description = "Used for loading cogs.", 
                      brief = "Loads cogs")
    @commands.is_owner()
    async def load(self, ctx, *, cogs: str = None):
        if cogs:
            cogs = cogs.split()
        else:
            cogs = ctx.bot.all_cogs()

        preloaded = []
        loaded = []
        not_found = []
        
        for cog in cogs:
            cog_name = self.cog_cleaner(cog.lower()).capitalize()
            if cog_name != "General" and cog_name != "":
                try:
                    await ctx.bot.load_extension(f'cogs.{cog_name}')
                    if cog_name not in loaded:
                        loaded.append(cog_name)
                except commands.ExtensionNotFound:
                    if cog_name not in not_found:
                        not_found.append(cog_name)
                except commands.ExtensionAlreadyLoaded:
                    if cog_name not in preloaded:
                        preloaded.append(cog_name)
        if loaded:
            loaded_e = discord.Embed(title = 'Loaded Cogs', 
                                     description = " ". join(f'`{cog}`' for cog in loaded), 
                                     color = self.green)
            await ctx.send(embed = loaded_e)
        
        if preloaded:
            preloaded_e = discord.Embed(title = 'Already Loaded Cogs', 
                                        description = " ".join(f'`{cog}`' for cog in preloaded), 
                                        color = discord.Color.purple())
            await ctx.send(embed = preloaded_e)

        if not_found:
            not_found_e = discord.Embed(title = "Invalid Cogs", 
                                        description = " ".join(f'`{cog}`' for cog in not_found), 
                                        color = self.red)
            await ctx.send(embed = not_found_e)

        return

    # 1) Make it so that any string variation can be read - Done
    @commands.command(aliases = ['r'],
                      help = "**Owner only**", 
                      description = "Used for reloading cogs.", 
                      brief = "Reloads cogs")
    @commands.is_owner()
    async def reload(self, ctx, *, cogs: str = None):
        if cogs:
            cogs = cogs.split()
        else:
            cogs = ctx.bot.all_cogs()

        reloaded = []
        unreloadable = []

        for cog in cogs:
            cog_name = self.cog_cleaner(cog.lower()).capitalize()
            if cog_name != "":
                try:
                    await ctx.bot.reload_extension(f'cogs.{cog_name}')
                    if cog_name not in reloaded:
                        reloaded.append(cog_name)
                except commands.ExtensionNotLoaded:
                    if cog_name not in unreloadable:
                        unreloadable.append(cog_name)

        if reloaded:
            reloaded_e = discord.Embed(title = "Reloaded Cogs", 
                                       description = " ".join(f'`{cog}`' for cog in reloaded), 
                                       color = self.green)
            await ctx.send(embed = reloaded_e)

        if unreloadable:
            unreloadable_e = discord.Embed(title = "Disabled/Unloadable Cogs", 
                                           description = " ".join(f'`{cog}`' for cog in unreloadable), 
                                           color = self.red)
            await ctx.send(embed = unreloadable_e)

        return
        
    @commands.command(aliases = ['u'],
                      help = "**Owner only**", 
                      description = "Used for unloading cogs.", 
                      brief = "Unloads cogs")
    @commands.is_owner()
    async def unload(self, ctx, *, cogs: str = None):
        if cogs:
            cogs = cogs.split()
        else:
            cogs = ctx.bot.all_cogs()

        unloaded = []
        invalid = []

        for cog in cogs:
            cog_name = self.cog_cleaner(cog.lower()).capitalize()
            if cog_name != "General" and cog_name != "":
                try:
                    await ctx.bot.unload_extension(f'cogs.{cog_name}')
                    if cog_name not in unloaded:
                        unloaded.append(cog_name)
                except commands.ExtensionNotLoaded:
                    if cog_name not in invalid:
                        invalid.append(cog_name)

        if unloaded:
            unloaded_e = discord.Embed(title = "Unloaded Cogs", 
                                       description = " ".join(f'`{cog}`' for cog in unloaded), 
                                       color = self.green)
            await ctx.send(embed = unloaded_e)

        if invalid:
            invalid_e = discord.Embed(title = "Invalid/Already Loaded Cogs", 
                                      description = " ".join(f'`{cog}`' for cog in invalid), 
                                      color = self.red)
            await ctx.send(embed = invalid_e)
        return

    @commands.command(aliases = ['sc', 'showcogs'], 
                      help = "**Owner only**", 
                      description = "Displays loaded & unloaded cogs.", 
                      brief = "Displays cogs")
    @commands.is_owner()
    async def cogs(self, ctx):
        loaded_cogs = [cog for cog, _ in ctx.bot.cogs.items()]
        all_cogs = ctx.bot.all_cogs()

        unloaded_cogs = []
        for cog in all_cogs:
            if cog not in loaded_cogs:
                unloaded_cogs.append(cog)

        if loaded_cogs:
            loaded_e = discord.Embed(title = "Currently Loaded Cogs", 
                                     description = " ".join(f'`{cog}`' for cog in loaded_cogs), 
                                     color = self.green)
            await ctx.send(embed = loaded_e)
        
        if unloaded_cogs:
            unloaded_e = discord.Embed(title = "Currently Unloaded Cogs", 
                                       description = " ".join(f'`{c}`' for c in unloaded_cogs), 
                                       color = self.red)
            await ctx.send(embed = unloaded_e)
        return

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))