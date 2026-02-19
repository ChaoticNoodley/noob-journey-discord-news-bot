import discord
from discord.ext import tasks, commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv
from news_fetcher import NewsFetcher
import asyncio

# configs
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))

SENT_NEWS_FILE = "sent_news.json"
CONFIG_FILE = "server_config.json"

# utilities
def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        with open(SENT_NEWS_FILE, "r") as f:
            return json.load(f)
    return []

def save_sent_news(sent_list):
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-200:], f, indent=4)

def load_configs():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_configs(configs):
    with open(CONFIG_FILE, "w") as f:
        json.dump(configs, f, indent=4)

# MAIN
class NewsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True

        super().__init__(command_prefix=None, intents=intents, help_command=None)

        self.tree = app_commands.CommandTree(self)
        self.fetcher = NewsFetcher()
        self.sent_news = load_sent_news()
        self.configs = load_configs()

        self.status_list = [
            "Modificando o Proton",
            "Lendo RSS",
            "Compilando Kernel",
            "Servindo notícias quentinhas ☕",
            "/help"
        ]
        self.status_index = 0

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands sincronizados")
        self.check_news.start()
        self.rotate_status.start()

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.user}")

    @tasks.loop(seconds=60)
    async def rotate_status(self):
        await self.wait_until_ready()
        activity = discord.Game(name=self.status_list[self.status_index])
        await self.change_presence(activity=activity)
        self.status_index = (self.status_index + 1) % len(self.status_list)

    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_news(self):
        await self.wait_until_ready()

        for guild_id, config in list(self.configs.items()):
            channel_id = config.get("channel_id")
            if not channel_id:
                continue

            try:
                channel = await self.fetch_channel(channel_id)
            except:
                continue

            categories = []
            if config.get("windows"): categories.append("windows")
            if config.get("linux"): categories.append("linux")

            for category in categories:
                news_items = self.fetcher.fetch_latest_news(category)

                for item in reversed(news_items):
                    if item["id"] not in self.sent_news:
                        await self.post_news(channel, item, guild_id)
                        self.sent_news.append(item["id"])
                        save_sent_news(self.sent_news)
                        await asyncio.sleep(5)

    async def post_news(self, channel, item, guild_id):
        config = self.configs.get(str(guild_id), {})
        roles = config.get("roles", {})
        role_ids = roles.get(item["category"], [])
        role_mentions = " ".join(f"<@&{rid}>" for rid in role_ids)

        color = discord.Color.blue() if item["category"] == "windows" else discord.Color.orange()

        embed = discord.Embed(
            title=item["title"],
            url=item["link"],
            description=item["summary"],
            color=color
        )

        if item.get("image_url"):
            embed.set_image(url=item["image_url"])

        embed.set_footer(text=f"Fonte: {item['category']} | {item['published']}")

        await channel.send(
            content=f"🔔 **Breaking News!** {role_mentions}",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )


bot = NewsBot()

# /Commands

@bot.tree.command(name="setchannel", description="Define o canal de notícias")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction):
    gid = str(interaction.guild.id)

    bot.configs.setdefault(gid, {})
    bot.configs[gid]["channel_id"] = interaction.channel.id
    bot.configs[gid]["windows"] = True
    bot.configs[gid]["linux"] = True
    save_configs(bot.configs)

    await interaction.response.send_message(
        f"✅ Canal configurado: {interaction.channel.mention}",
        ephemeral=True
    )


@bot.tree.command(name="showconfig", description="Mostra a configuração do servidor")
async def showconfig(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    config = bot.configs.get(guild_id)

    if not config:
        await interaction.response.send_message("Servidor não configurado.", ephemeral=True)
        return

    channel = bot.get_channel(config["channel_id"])
    channel_name = channel.mention if channel else "Canal inválido"

    await interaction.response.send_message(
        f"📡 **Configuração atual:**\n"
        f"Canal: {channel_name}\n"
        f"Windows: {config.get('windows')}\n"
        f"Linux: {config.get('linux')}",
        ephemeral=True
    )


@bot.tree.command(name="testnews", description="Testa envio de notícias")
@app_commands.checks.has_permissions(administrator=True)
async def testnews(interaction: discord.Interaction):
    await interaction.response.send_message("🔎 Testando envio...", ephemeral=True)

    for cat in ["windows", "linux"]:
        news = bot.fetcher.fetch_latest_news(cat, limit=1)
        if news:
            await bot.post_news(interaction.channel, news[0], str(interaction.guild.id))


@bot.tree.command(name="latest", description="Mostra a última notícia")
@app_commands.describe(category="windows ou linux")
async def latest(interaction: discord.Interaction, category: str):
    category = category.lower()

    if category not in ["windows", "linux"]:
        await interaction.response.send_message("Use windows ou linux", ephemeral=True)
        return

    news = bot.fetcher.fetch_latest_news(category, limit=1)
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


# run bot
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN não encontrado")
    else:
        bot.run(TOKEN)
