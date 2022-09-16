import discord
from discord.ext import commands
from discord import Spotify, Game, ActivityType, app_commands
from datetime import datetime, timezone

class Custom(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # 1) Make it allow for mentions - Done
    # 2) Handle status & activities - Done
    @commands.command(aliases = ['uinfo'])
    async def userinfo(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        name = member.name
        nick = member.nick
        disc = member.discriminator
        created = member.created_at
        joined = member.joined_at
        status = member.status
        activities = member.activities
        roles = sorted([r for r in member.roles if r.name != "@everyone"], key = lambda role: role.position, reverse = True)
        avatar = member.avatar
        display_avatar = member.display_avatar

        # Status + Activities
        activity = f'**{status.name.upper()}**'
        for a in activities:
            if isinstance(a, Spotify):
                activity += f'\nListening to **{a.title}** - **{a.artist}**'
            elif a.type == ActivityType.playing:
                activity += f'\nPlaying **{a.name}**' + ("" if isinstance(a, Game) else f' - **{a.details}**' if a.details else "")
            elif a.type == ActivityType.streaming:
                activity += f'\nStreaming **{a.name}**'
            elif a.type == ActivityType.watching:
                activity += f'\nWatching **{a.name}**'
            elif a.type == ActivityType.competing:
                activity += f'\nCompeting in **{a.name}**'
            elif a.type == ActivityType.custom:
                activity += "\n**"
                if a.emoji:
                    activity += f'{a.emoji}'
                if a.name:
                    activity += a.name
                activity += "**"

        # Time Conversions to local user time
        now = datetime.now().astimezone()
        created = created.replace(tzinfo=timezone.utc).astimezone(tz=now.tzinfo)
        joined = joined.replace(tzinfo=timezone.utc).astimezone(tz=now.tzinfo)
        date_fmt = "%b %d, %Y %I:%M %p"

        # Username + Avatar
        username = f'{name}#{disc}' + (f' AKA {nick}' if nick else "")
        e = discord.Embed(title = username, description = activity, color = roles[0].color if roles else 0x3498db)
        e.set_thumbnail(url = display_avatar if display_avatar else avatar)
        
        # Create Date
        e.add_field(name = f'**Account Created**', value = f'{created.strftime(date_fmt)} \n {(now - created).days} days ago', inline = True)

        # Join Date
        e.add_field(name = f'**Joined Server**', value = f'{joined.strftime(date_fmt)} \n {(now - joined).days} days ago', inline = True)

        # Roles
        e.add_field(name = "**Roles**", value = " ".join(f'{r.mention}' for r in roles) if roles else None, inline = False)

        # Member ID + Join Position
        e.set_footer(text = f'Member #{ctx.guild.members.index(member) + 1} | ID: {member.id}')

        return await ctx.reply(embed = e, mention_author = False)

    @userinfo.error
    async def userinfo_err(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            return await ctx.send("User is not in the server.")

    @commands.command(aliases = ['sinfo'])
    async def serverinfo(self, ctx):
        guild = ctx.guild
        guild_id = guild.id
        name = guild.name
        members = len(guild.members)
        owner = guild.owner
        created = guild.created_at
        icon = guild.icon.url
        roles = sorted([r for r in guild.roles if r.name != "@everyone"], key = lambda role: role.position, reverse = True)

        now = datetime.now().astimezone()
        created = created.replace(tzinfo=timezone.utc).astimezone(tz=now.tzinfo)
        date_fmt = "%b %d, %Y %I:%M %p"

        e = discord.Embed(title = f'**{name}**', color = roles[0].color if roles else 0x3498db)
        e.set_thumbnail(url = icon)

        # Creation Date
        e.add_field(name = "**Guild Created**", value = f'{created.strftime(date_fmt)} \n {(now - created).days} days ago', inline = True)

        # Owner
        e.add_field(name = "**Owner**", value = f'{owner.mention}', inline = True)

        # Member Count
        e.add_field(name = "**Members**", value = f'{members}', inline = True)

        # Roles
        e.add_field(name = "**Roles**", value = " ".join([f'{r.mention}' for r in roles]), inline = False) 

        # Footer - Guild ID
        e.set_footer(text = f'Guild ID: {guild_id}')

        return await ctx.reply(embed = e, mention_author = False)

    @commands.command(aliases = ['say'],
                      help = "",
                      description = "",
                      brief = "")
    async def echo(self, ctx, *, msg: str):
        return await ctx.send(f"{msg}")

    # @commands.command(aliases = ['google', 'lookup'], 
    #                   help = "",
    #                   description = "",
    #                   brief = "")
    # @app_commands.command(name = "google", description = "What you wanted to lookup from Google")
    # async def search(self, interaction: discord.Interaction, *query):
    #     e = discord.Embed(title = " ".join(query), 
    #                       description = "What you wanted to lookup from Google",
    #                       url = "https://www.google.com/search?q=" + "+".join(query),
    #                       color = 0x3498db)
    #     # return await ctx.send(embed = e)
    #     return await interaction.response.send_message(embed = e)

    # Custom Commands
    @commands.command(help = "",
                      description = "",
                      brief = "")
    @commands.has_permissions(manage_channels = True, manage_messages = True, manage_permissions = True)
    async def cc(self, ctx, message):
        return

    # Math
    @commands.command(help = "",
                      description = "",
                      brief = "")
    async def ev(self, ctx, message):
        return

    # Pinging + Command Errors

    @commands.command(aliases = ['mention'],
                      help = "", 
                      description = "Used when you're too lazy to right click someone.",
                      brief = "")
    async def ping(self, ctx, *, member: discord.Member = None):
        member_id = member.id
        username = member.name
        if member_id != ctx.bot.user.id or username != ctx.bot.user.name:
            return await ctx.send(member.mention)
        elif not member:
            return await ctx.send("User is not in the server.")
        else:
            return await ctx.send("Nice try pinging me. :smirk:")

    @ping.error
    async def ping_error(self, ctx, error: commands.CommandError):
        if isinstance(error, commands.BadArgument):
            return await ctx.send("``` User not found. Please input someone in the server!```")

async def setup(bot: commands.Bot):
    await bot.add_cog(Custom(bot))