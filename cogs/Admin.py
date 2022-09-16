import discord
import discord.errors
from discord.ext import commands
from asyncio import TimeoutError, sleep

class Admin(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.YES = "✅"
        self.NO = "❌"

    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        return

    @commands.Cog.listener()
    async def on_guild_channel_create(self, c):
        mute_role = discord.utils.get(c.guild.roles, name = 'Muted')
        if not mute_role:
            mute_role = await self.make_mute_role(c.guild.id)
        await c.set_permissions(mute_role, send_messages = False, read_messages = False)

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction, user):
    #     if user == self.bot.user:
    #         return
    #     try:
    #         if not self.bot.user in [u async for u in reaction.users()]:
    #             return
    #     except discord.errors.NotFound:
    #         return

    #     msg = reaction.message
    #     ctx = await self.bot.get_context(msg)
        
    #     if reaction.emoji == self.YES:
    #         if "delete" in msg.content:
    #             msg_amount = int(msg.content.split()[7])
    #             await ctx.channel.purge(limit = msg_amount + 2)
    #             return await ctx.send(f"{msg_amount} messages have been deleted.")

    #     if reaction.emoji == self.NO:
    #         if "delete" in msg.content:
    #             return await ctx.send("No messages have been deleted.")

    def username_filter(self, user: str):
        return ''.join(filter(str.isalpha, user))

    # 1) Make channels change perms for 'Muted' Role
    async def make_mute_role(self, guild_id):
        guild = await self.bot.fetch_guild(guild_id)
        try:
            mute_role = await guild.create_role(name = 'Muted', mentionable = True, hoist = True, color = 0x0c0c0c)
            for channel in guild.channels:
                await channel.set_permissions(mute_role, read_messages = False, send_messages = False)
            return mute_role
        except discord.errors.Forbidden:
            return await self.bot.send("```Unable to create 'Muted' role in this server.```")

    # 1) Need to make it so that I can mute/unmute - Done through roles
    # 2) Mute/unmute typing - Done
    # 3) Find the role used to mute - Done
    # 4) Make it so I can mute/unmute multiple members - Requires that I remove mute reason
    @commands.command(help = "Must have **<Manage Roles>** Permission.", 
                      description = "Mutes user through a 'Muted' role.", 
                      brief = "Mutes User")
    @commands.has_permissions(manage_roles = True)
    async def mute(self, ctx, member: discord.Member, *, mute_reason: str = None):
        if member.id == self.bot.user.id or member.id == ctx.author.id:
            return
        if member.top_role >= ctx.author.top_role:
            return await ctx.reply("```You cannot mute someone with a higher/equal role than you!```", mention_author = False)
        
        role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
        if not role:
            role = await self.make_mute_role(ctx.message.guild.id)
        
        if role and role not in member.roles:
            await member.add_roles(role, reason = mute_reason)
            muted_e = discord.Embed(title = f'{member.name} has been muted.', 
                                    description = f'{member.mention} was muted by {ctx.message.author.mention}.', 
                                    color = 0x3498db)
            muted_e.set_footer(text = f'Reason: {mute_reason}')
            return await ctx.reply(embed = muted_e, mention_author = False)
        else:
            return await ctx.send(f'{member.mention} is already muted!')

    @mute.error
    async def mute_err(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("```You cannot mute someone who is not in the server.```", mention_author = False)

    @commands.command(help = "Must have **<Manage Roles>** Permission.", 
                      description = "Unmutes user by taking away 'Muted' role.", 
                      brief = "Unmutes User")
    @commands.has_permissions(manage_roles = True)
    async def unmute(self, ctx, member: discord.Member = None, *, unmute_reason: str = None):
        if member.id == self.bot.user.id or member.id == ctx.author.id:
            return
        if member.top_role >= ctx.author.top_role:
            return await ctx.reply("```You cannot unmute someone with a higher role than you!```", mention_author = False)
        role = discord.utils.get(ctx.message.guild.roles, name = "Muted")
        if not role:
            await ctx.reply(f'Muted role does not exist. It will be created now.', mention_author = False)
            await self.make_mute_role(ctx.message.guild.id)
            return
        
        if role in member.roles:
            await member.remove_roles(role)
            unmute_e = discord.Embed(title = f'{member.name} has been unmuted.',
                                     description = f'{member.mention} was unmuted by {ctx.message.author.mention}.', 
                                     color = 0x3498db)
            unmute_e.set_footer(text = f"Reason: {unmute_reason}")
            return await ctx.reply(embed = unmute_e, mention_author = False)
        else:
            return await ctx.send(f'{member.mention} has not been muted.')

    @unmute.error
    async def unmute_err(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("```You cannot unmute someone who is not in the server.```", mention_author = False)

    # Kicking & Banning
    # 1) Make so it can kick/ban however many users entered
    @commands.command(help = "Must have **<Kick Members>** Permission.", 
                      description = "Kicks a user in the server.", 
                      brief = "Kicks User(s)")
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member:discord.Member = None, *, kick_reason = None):
        if member.id == self.bot.user.id or member.id == ctx.author.id:
            return
        if member.top_role >= ctx.author.top_role:
            return await ctx.reply("```You cannot kick someone with a higher/similar role than you!```", mention_author = False)

        await member.kick(reason = kick_reason)
        kick_e = discord.Embed(title = f"{member.name} has been kicked.",
                               description = f'{member.mention} has been kicked by {ctx.message.author.mention}.',
                               color = 0x3498db)
        kick_e.set_footer(text = f'Reason: {kick_reason}')
        return await ctx.reply(embed = kick_e, mention_author = False)

    @kick.error
    async def kick_error(self, ctx, error: commands.CommandError):
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("```You cannot kick this person as they are not in the server.```", mention_author = False)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("```You do not have access to this command.```", mention_author = False)

    # 1) Convert ban to apply to DISCORD USERS (Use ids) - Done
    @commands.command(help = "Must have **<Ban Members>** Permission.", 
                      description = "Bans a user from the server.", 
                      brief = "Bans User(s)")
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, user:discord.User = None, *, ban_reason = None):
        if user.id == self.bot.user.id or user.id == ctx.author.id or user.id == ctx.guild.owner_id:
            return
        member = ctx.guild.get_member(user.id)
        if member and member.top_role >= ctx.author.top_role:
            return await ctx.reply("```You cannot ban someone with a higher/similar role than you!```", mention_author = False)

        await ctx.guild.ban(user, reason = ban_reason)
        ban_e = discord.Embed(title = f'{user.name} has been banned.',
                              description = f'{user.mention} has been banned by {ctx.message.author.mention}.',
                              color = 0x3498db)
        ban_e.set_footer(text = f'Reason: {ban_reason}')
        return await ctx.reply(embed = ban_e, mention_author = False)

    @ban.error
    async def ban_error(self, ctx, error: commands.CommandError):
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("```You cannot ban this person as they are not in the server.```", mention_author = False)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("```You do not have access to this command.```", mention_author = False)

    # Unbanning
    # 1) Implement id unbans to work with name unbans - Done?
    @commands.command(help = "Must have **<Ban Members>** Permission.", 
                      description = "Unbans a user from the server.", 
                      brief = "Unbans User(s)")
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, member: str, *, unban_reason: str = None):
        if "#" in member:
            member_name, discriminator = member.split("#")
            async for ban in ctx.guild.bans(limit = 100):
                user = ban.user
                if (user.name, user.discriminator) == (member_name, discriminator):
                    await ctx.guild.unban(user)
                    unban_e = discord.Embed(title = f'{member_name}#{discriminator} has been unbanned.',
                                            description = f'{member_name} has been unbanned by {ctx.message.author.mention}.',
                                            color = 0x3498db)
                    unban_e.set_footer(text = f'Reason: {unban_reason}')
                    return await ctx.reply(embed = unban_e, mention_author = False)
                else:
                    return await ctx.send("```User has not been banned or does not exist in this server.```")
        else:
            try:
                member = await ctx.bot.fetch_user(int(member))
                await ctx.guild.unban(member)
                unban_e = discord.Embed(title = f'{member.name} has been unbanned.',
                                        description = f'{member.mention} has been unbanned by {ctx.message.author.mention}.',
                                        color = 0x3498db)
                unban_e.set_footer(text = f'Reason: {unban_reason}')
                return await ctx.reply(embed = unban_e, mention_author = False)
            except:
                return await ctx.send("```User may not be banned or the input is not a valid username with tag or id.```")

    @unban.error
    async def unban_err(self, ctx, error):        
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("You do not have access to this command.", mention_author = False)

    # Deleting messages
    # 1) Add way to confirm if deleting is desired - Done
    # 2) Allow for pruning of member specific messages - Done
    @commands.command(aliases = ['prune', 'purge'], 
                      help = "Must have **<Manage Messages>** Permission.", 
                      description = "Cleaning up channels!", 
                      brief = "Deletes messages")
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, *query):
        mentions = ctx.message.mentions
        await ctx.message.delete()
        try:
            msg_amount = int(query[-1])
        except:
            return await ctx.send("Please enter the **amount** of messages you wish to delete.")

        if msg_amount <= 0:
            return await ctx.send("Please enter a number **greater than 0**.")

        if not mentions:
            confirm_e = discord.Embed(title = f"Are you sure you want to delete {msg_amount} messages?", color = discord.Color.purple())
            confirm = await ctx.send(embed = confirm_e)
            await confirm.add_reaction(self.YES)
            await confirm.add_reaction(self.NO)

            check = lambda reaction, user: user.id == ctx.author.id and reaction.message.channel.id == ctx.channel.id and (reaction.emoji == self.YES or reaction.emoji == self.NO)
            
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check = check, timeout = 15.0)
            except TimeoutError:
                timeout_e = discord.Embed(title = f"No response from {ctx.author.name}. Clearing has been aborted.", color = 0xe61212)
                return await ctx.send(embed = timeout_e)

            reaction_e = discord.Embed()
            if reaction.emoji == self.YES:
                if msg_amount > 1:
                    reaction_e.title = f"{msg_amount} messages have been deleted by {user.name}."
                else:
                    reaction_e.title = f"{msg_amount} message has been deleted by {user.name}."
                reaction_e.color = 0x3498db
                await ctx.channel.purge(limit = msg_amount + 2)
                return await ctx.reply(embed = reaction_e, mention_author = False)
            else:
                reaction_e.title = f"No messages have been deleted."
                reaction_e.color = 0xe61212
                return await ctx.reply(embed = reaction_e, mention_author = False)

        total_del = 0

        for u in mentions:
            if u.top_role >= ctx.author.top_role and u.id != ctx.author.id and u.id != ctx.bot.user.id:
                continue
            deleted = 0
            async for msg in ctx.channel.history(limit = 100):
                if msg.author.id == u.id and deleted < msg_amount:
                    await msg.delete()
                    await sleep(delay = 0.85)
                    deleted += 1
                if deleted == msg_amount:
                    pass
            total_del += deleted
        
        res_e = discord.Embed(title = f'Total Messages Deleted: {total_del}',
                              description = f'**Deleted from:** _{" ".join([u.name for u in mentions])}_',
                              color = 0x3498db)
        res_e.set_footer(text = f'Done by: {ctx.author.name}')
        return await ctx.reply(embed = res_e, mention_author = False)
                
    @clear.error
    async def clear_err(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            return await ctx.reply("Please enter the **amount** of messages to clear!", mention_author = False)
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("```You do not have access to this command.```", mention_author = False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))