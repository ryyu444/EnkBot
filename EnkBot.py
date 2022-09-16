import discord
from discord.ext import commands
from discord.errors import Forbidden
from typing import Optional, Literal
import logging
import os

# Logging Stuff: Set log_handler = None in super().__init__ if I want to manually handle logging
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# Actual Bot - Rewrite into a class

description = "Thank you for inviting me! Please use '!' to execute commands."

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

class EnkBot(commands.Bot):

    # Start Up
    def __init__(self):
        super().__init__(command_prefix = "!", description = description, intents = intents, help_command = None, activity = discord.Game(name = "In testing!"))

    def all_cogs(self):
        return [f[:-3] for f in os.listdir(os.getenv('COG_DIR')) if f.endswith('.py')]

    def loaded_cogs(self, lower = False):
        return [c.lower() if lower else c for c in self.cogs]

    async def load_cogs(self):
        cogs = self.all_cogs()
        for cog in cogs:
            try:
                await self.load_extension(f'cogs.{cog}')
            except:
                pass
    
    async def joined_guilds(self):
        return await [g async for g in self.fetch_guilds(limit = 100)]
    
    # 1) Set perms for channels
    @commands.has_permissions(manage_roles = True)
    async def new_role_creator(self, guild):
        guild = await self.fetch_guild(guild)
        new_role = await guild.create_role(name = 'New', mentionable = True, hoist = True, color = 0xFF0000)
        perms = discord.Permissions()
        perms.update(read_messages = True, send_messages = True, read_message_history = True)
        await new_role.edit(permissions = perms)
        return new_role

    async def setup_hook(self) -> None:
        for c in DEFAULT_COMMANDS:
            self.add_command(c)
        await self.load_cogs()

    async def on_ready(self):
        print(f"Logging in as {self.user.name}: ID - {self.user.id}")

    # Bot Events
    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        process = True
        if process:
            await self.process_commands(message)
    
    async def on_member_join(self, member: discord.Member):
        role = discord.utils.get(member.guild.roles, name = 'New')
        if not role:
            role = await self.new_role_creator(member.guild.id)
        try:
            await member.add_roles(role)
            join_e = discord.Embed(title = f'Welcome {member.name} to {member.guild}!', 
                                   description = 'We hope you enjoy your stay. :heart:', 
                                   color = 0x3498db)
            return await member.send(embed = join_e)
        except Forbidden:
            return
    
    async def on_member_remove(self, member: discord.User):
        user = await self.fetch_user(member.id)
        try:
            leave_e = discord.Embed(title = f'Goodbye {member.name}!', 
                                    description = "Sad to see you leave :frowning:", 
                                    color = discord.Color.fuchsia())
            return await user.send(embed = leave_e)
        except Forbidden:
            return

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return await ctx.send("Command does not exist.")
    
    def _run(self):
        self.run(os.getenv('TOKEN'))

# EVENTS
# 1) @bot.event
# 2) async def on_(function name - look at docs)

# COMMANDS
# 1) @bot.command(aliseses = [], name = (whatever you want to run the command with))
# 2) async def func(ctx, other args)
# 3) Use * before an arg to read it all into one var // Use *arg to get a tuple with input separated

# COGS
# 1) Create separate file in cogs
# 2) Have a setup function (async def setup(bot): await bot.add_cog(Class, bot))

# Help Command
@commands.command(description = "Used for looking up bot features!", 
                  help = "!help <cog/cmd>, arguments are not case sensitive.")
async def help(ctx, *, args: str = None):
    if not args:
        return await send_bot_help(ctx)
    else:
        args = args.lower()
        for name, cog in ctx.bot.cogs.items():
            if name.lower() == args:
                return await send_cog_help(ctx, cog)
        for cmd in ctx.bot.commands:
            if args == cmd.name or (cmd.aliases and args in cmd.aliases):
                try:
                    if cmd.commands:
                        return await send_group_help(ctx, cmd)
                except:
                    return await send_command_help(ctx, cmd)
    return await ctx.send("Invalid Cog or Command.")

async def send_bot_help(ctx):
    e = discord.Embed(title = "EnkBot Help")
    e.description = "\n".join([f'*{c}*' for c in ctx.bot.all_cogs()])
    e.set_footer(text = "!help <cog> for more details!")
    e.color = 0x3498db
    await ctx.send(embed = e)

# 1) Include briefs for each cog - Done
async def send_cog_help(ctx, cog):
    e = discord.Embed(title = f'{cog.qualified_name} Help',
                      color = 0x3498db)
    e.description = "\n".join([f'**{cmd.name}**: {cmd.brief}' for cmd in cog.get_commands()])
    e.set_footer(text = "!help <cmd> for more details!")
    await ctx.send(embed = e)

async def send_group_help(ctx, group):
    e = discord.Embed(title = f'{group.name} subcommands',
                      color = 0x3498db)
    e.description = group.description
    for c in group.commands:
        e.add_field(name = f'{group.name} {c.name}', 
                    value = c.description, 
                    inline = True)
    await ctx.send(embed = e)

async def send_command_help(ctx, command):
    e = discord.Embed(title = f'!{command.name} {command.signature}',
                      color = 0x3498db)
    e.add_field(name = "Description", 
                value = command.description, 
                inline = True)
    e.add_field(name = "Help", 
                value = command.help, 
                inline = False)
    if command.aliases:
        e.set_footer(text = f'Aliases: {" ".join(command.aliases)}')
    await ctx.send(embed = e)

@commands.command()
async def test1(ctx, *arg1):
    args = 0
    for arg in arg1:
        await ctx.send(arg)
        args += 1
    return await ctx.send(f'{args} printed.')

@commands.command()
async def test2(ctx, *, arg1):
    await ctx.send(arg1)
    await ctx.message.delete()

@commands.is_owner()
@commands.command()
async def sync(ctx, guilds: commands.Greedy[discord.Object], choice: Optional[Literal["cur"]] = None) -> None:
    if not guilds:
        if not choice:
            ctx.bot.tree.copy_global_to(guild = ctx.guild)
            cmds = await ctx.bot.tree.sync(guild = ctx.guild)
            return await ctx.send(f'Synced {len(cmds)} **global commands** to {ctx.guild.name}.')
        elif choice == "cur": # Requires global commands to be sync'd to guild first
            cmds = await ctx.bot.tree.sync(guild = ctx.guild)
            return await ctx.send(f"Synced {len(cmds)} commands to {ctx.guild.name}.")
        else: # Sync globally once
            cmds = await ctx.bot.tree.sync()
            return await ctx.send(f"Synced {len(cmds)} commands to all guilds.")

    synced = 0
    for g in guilds:
        try:
            ctx.bot.tree.copy_global_to(guild = discord.Object(id = g))
            await ctx.bot.tree.sync(guild = discord.Object(id = g))
            synced += 1
        except discord.HTTPException:
            pass

    return await ctx.send(f"Synced **all global commands** to {synced} guilds.")

@commands.is_owner()
@commands.command()
async def unsync(ctx, guilds: commands.Greedy[discord.Object], choice: Optional[Literal["all"]] = None) -> None:
    if not guilds:
        if not choice:
            ctx.bot.tree.clear_commands(guild = ctx.guild)
            await ctx.bot.tree.sync(guild = ctx.guild)
            return await ctx.send(f"Unsynced **all global commands** from {ctx.guild.name}.")
        else:
            ctx.bot.tree.clear_commands()
            await ctx.bot.tree.sync()
            return await ctx.send(f'Unsynced **all global commands** for all guilds.')

    unsynced = 0
    for g in guilds:
        try:
            ctx.bot.tree.clear_commands(guild = discord.Object(id = g))
            await ctx.bot.tree.sync(guild = discord.Object(id = g))
            unsynced += 1
        except discord.HTTPException:
            pass

    return await ctx.send(f'Unsynced **all global commands to {unsynced} guilds.')


DEFAULT_COMMANDS = [test1, test2, help, sync, unsync]
EnkBot()._run()