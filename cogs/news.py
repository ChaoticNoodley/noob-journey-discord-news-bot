import discord
from discord import app_commands
from discord.ext import commands
import asyncio


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="testnews", description="Testa envio de notícias")
    @app_commands.checks.has_permissions(administrator=True)
    async def testnews(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔎 Testando envio...", ephemeral=True)

        for cat in ["windows", "linux"]:
            news = self.bot.fetcher.fetch_latest_news(cat, limit=1)
            if news:
                await self.bot.post_news(interaction.channel, news[0], str(interaction.guild.id))

    @app_commands.command(name="latest", description="Mostra a última notícia")
    @app_commands.describe(category="windows ou linux")
    async def latest(self, interaction: discord.Interaction, category: str):
        category = category.lower()

        if category not in ["windows", "linux"]:
            await interaction.response.send_message("Use windows ou linux", ephemeral=True)
            return

        news = self.bot.fetcher.fetch_latest_news(category, limit=1)
        if not news:
            await interaction.response.send_message("Nenhuma notícia encontrada.")
            return

        item = news[0]

        embed = discord.Embed(
            title=item["title"],
            url=item["link"],
            description=item["summary"],
            color=discord.Color.blue() if category == "windows" else discord.Color.orange()
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(News(bot))
