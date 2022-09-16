import discord
from discord import app_commands
from discord.ext import commands

class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
    
    @app_commands.command(name="command-1")
    async def my_commands(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hello from command 1!", ephemeral=True)

    @app_commands.command(name="command-2")
    async def my_private_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Hello from private command!", ephemeral=True)

    @app_commands.command(name = "google")
    async def search(self, interaction: discord.Interaction, *, query: str) -> None:
        query = query.split()
        e = discord.Embed(title = " ".join(query), 
                          description = "What you wanted to lookup from Google",
                          url = "https://www.google.com/search?q=" + "+".join(query),
                          color = 0x3498db)
        await interaction.response.send_message(embed = e)

    # Make it responsive with buttons
    @app_commands.command(name = "poll")
    async def create_poll(self, interaction: discord.Interaction, *, poll_title: str) -> None:
        e = discord.Embed(title = poll_title)

        await interaction.response.send_message(embed = e)

    @app_commands.command(name = "test")
    async def testing(self, interaction: discord.Interaction):
        await interaction.response.send_message("testing")

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Slash(bot))