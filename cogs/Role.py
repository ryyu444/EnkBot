import discord
import discord.errors
from discord.ext import commands

class Role(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases = ['mkr', 'rm'], 
                      help = "Must have **<Manage Roles>** Permission.", 
                      description = "Creates a specified role with optional display color (hexcode).", 
                      brief = "Creates New Role")
    @commands.has_permissions(manage_roles = True)
    async def makerole(self, ctx, *, role: str = None):
        guild = ctx.guild
        try:
            role_name, display_color = role.split("#")
        except:
            role_name, display_color = role, None
        if role_name:
            if display_color:
                await guild.create_role(name = role_name, mentionable = True, hoist = True, color = discord.Color.from_str(f'0x{display_color}'))
            else:
                await guild.create_role(name = role_name, mentionable = True, hoist = True, color = 0x32CD32)
            role_e = discord.Embed(title = f'{role_name} has been created!', 
                                   color = 0x3ecf43)
            return await ctx.reply(embed = role_e, mention_author = False)
        else:
            return await ctx.send(f'Please enter the name of the role you want to add and optionally the color in the form of **role#hexcode**.')

    @makerole.error
    async def makerole_err(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply(f'```You do not have the permissions to make a role.```')

    @commands.command(aliases = ['rmr', 'rd', 'dr'],
                      help = "Must have **<Manage Roles>** Permission.",
                      description = "Deletes a specified role if found in the server.",
                      brief = "Deletes Existing Role")
    @commands.has_permissions(manage_roles = True)
    async def deleterole(self, ctx, *, role_name: str = None):
        role = discord.utils.get(ctx.message.guild.roles, name = role_name)
        if not role:
            return await ctx.send(f'**{role_name}** is not a valid role to delete.')
        if role >= ctx.author.top_role or role >= ctx.guild.me.top_role: # Grabs bot's top role
            return await ctx.send(f'```Could not delete role due to role hierarchy.```')
        
        role_e = discord.Embed()
        try:
            await role.delete()
            role_e.title = f'{role_name} has been removed!'
            role_e.color = 0x3ecf43
            return await ctx.reply(embed = role_e, mention_author = False)
        except:
            role_e.title = f"{role_name} doesn't exist."
            role_e.color = 0xe61212
            return await ctx.send(embed = role_e)

    @deleterole.error
    async def deleterole_err(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply(f'```You do not have the permissions to delete a role.```', mention_author = False)
    
    # 1) Multiple Role addition/removal
    # 2) Deal with users not in server - Can be improved
    @commands.command(aliases = ['ar', 'ra'], 
                      help = "Must have **<Manage Roles>** Permission.",
                      description = "Gives a role to a specific user in the server.",
                      brief = "Adds role to User")
    @commands.has_permissions(manage_roles = True)
    async def addrole(self, ctx, member: discord.Member = None, role_name: str = None):
        role = discord.utils.get(ctx.message.guild.roles, name = role_name)
        if member:
            role_e = discord.Embed()
            mem_roles = [role.name for role in member.roles if role.name != "@everyone"]
            try:
                if role.name not in mem_roles:
                    await member.add_roles(role)
                    role_e.title = f"Roles successfully added for {member.name}."
                    role_e.color = 0x3ecf43
                    return await ctx.reply(embed = role_e, mention_author = False)
                else:
                    role_e.title = f"{member.name} already has {role.name}."
                    role_e.color = 0xe61212
                    return await ctx.reply(embed = role_e, mention_author = False)
            except:
                role_e.title = "Please input a valid role to give to the user."
                role_e.color = 0xe61212
                return await ctx.send(embed = role_e)
        else:
            return await ctx.send("```Please enter a user to give a role to.```")

    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("```You do not have the permissions to give roles to users.```", mention_author = False)
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply('```User is not is in the server.```', mention_author = False)

    @commands.command(aliases = ['rr'], 
                      help = "Must have **<Manage Roles>** Permission.",
                      description = "Removes a role from a specific user in the server",
                      brief = "Removes role from User")
    @commands.has_permissions(manage_roles = True)
    async def removerole(self, ctx, member: discord.Member = None, role_name: str = None):
        role = discord.utils.get(ctx.message.guild.roles, name = role_name)
        if member:
            role_e = discord.Embed()
            mem_roles = [role.name for role in member.roles if role.name != "@everyone"]
            try:
                if role.name in mem_roles:
                    await member.remove_roles(role)
                    role_e.title = f'Roles successfully removed for {member.name}.'
                    role_e.color = 0x3ecf43
                    return await ctx.reply(embed = role_e, mention_author = False)
                else:
                    role_e.title = f'{member.name} does not have {role.name}.'
                    role_e.color = 0xe61212
                    return await ctx.reply(embed = role_e, mention_author = False)
            except:
                role_e.title = "Please input a valid role that the user has to remove."
                role_e.color = 0xe61212
                return await ctx.send(embed = role_e)
        else:
            return await ctx.send("```Please enter a user to remove a role from.```")

    @removerole.error
    async def removerole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            return await ctx.reply("```You do not have the permissions to remove roles from users.```", mention_author = False)
        if isinstance(error, commands.MemberNotFound):
            return await ctx.reply("```User is not in the server.```", mention_author = False)

    @commands.command(name = 'roles', 
                      help = "Just roles. :smirk:",
                      description = "Displays all the existing roles in the server.",
                      brief = "Shows Server Roles")
    async def showRoles(self, ctx):
        roles = sorted([r for r in ctx.guild.roles if r.name != "@everyone"], key = lambda role: role.position, reverse = True)
        e = discord.Embed(title = "Role List", 
                          description = '\n'.join([f'{role.mention}' for role in roles if role.name != "@everyone"]), 
                          color = 0x3498db)
        return await ctx.reply(embed = e, mention_author = False)

async def setup(bot: commands.Bot):
    await bot.add_cog(Role(bot))