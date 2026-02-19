import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Mostra os comandos da Winux-chan")
    async def help_command(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🤖 Winux-chan Commands",
            description="Bot de notícias sobre Windows & Linux",
            color=discord.Color.purple()
        )

        embed.set_image(url="https://imgur.com/zHHSPx9.gif")

        embed.add_field(
            name="📡 Configuração",
            value=
            "`/setchannel` - Define o canal atual\n"
            "`/showconfig` - Mostra a configuração da Winux-chan\n"
            "`/setrole windows @Role` - Adiciona cargo p/ Windows\n"
            "`/setrole linux @Role` - Adiciona cargo p/ Linux\n"
            "`/removerole windows @Role` - Remove cargo\n"
            "`/clearroles` - Limpa todos os cargos\n"
            "`/showroles` - Mostra cargos configurados",
            inline=False
        )

        embed.add_field(
            name="🧪 Outros",
            value=
            "`/testnews` - Testa o envio manual\n"
            "`/say <msg>` - Faz o bot falar\n"
            "`/latest windows|linux` - Última notícia\n"
            "`/help` - Mostra este menu",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Help(bot))
