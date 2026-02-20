import discord
from discord import app_commands
from discord.ext import commands


class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="say", description="Faz o bot falar uma mensagem")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def say(self, interaction: discord.Interaction, message: str):
        await interaction.channel.send(message)
        await interaction.response.send_message("✅ Mensagem enviada!", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Say(bot))
