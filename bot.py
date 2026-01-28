import discord
from discord.ext import tasks, commands
import os
import json
from dotenv import load_dotenv
from news_fetcher import NewsFetcher
import asyncio

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ROLE_LINUX_ID = int(os.getenv("ROLE_LINUX_ID", 0))
ROLE_WINDOWS_ID = int(os.getenv("ROLE_WINDOWS_ID", 0))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))

SENT_NEWS_FILE = "sent_news.json"


def load_sent_news():
    if os.path.exists(SENT_NEWS_FILE):
        with open(SENT_NEWS_FILE, "r") as f:
            return json.load(f)
    return []


def save_sent_news(sent_list):
    with open(SENT_NEWS_FILE, "w") as f:
        json.dump(sent_list[-100:], f)


class NewsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix="!", intents=intents)

        self.fetcher = NewsFetcher()
        self.sent_news = load_sent_news()

    async def setup_hook(self):
        # Inicia a task (sem wait_until_ready aqui)
        self.check_news.start()

    async def on_ready(self):
        print("ON_READY disparou")
        print(f"Bot conectado como {self.user}")

        # Debug: testar canal
        try:
            channel = await self.fetch_channel(CHANNEL_ID)
            print(f"Canal encontrado: {channel.name}")
        except Exception as e:
            print(f"Erro ao buscar canal no on_ready: {e}")

    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_news(self):
        try:
            channel = await self.fetch_channel(CHANNEL_ID)
        except discord.NotFound:
            print(f"Canal {CHANNEL_ID} não encontrado.")
            return
        except discord.Forbidden:
            print("Sem permissão para acessar o canal.")
            return
        except discord.HTTPException as e:
            print(f"Erro HTTP ao buscar canal: {e}")
            return

        for category in ["windows", "linux"]:
            news_items = self.fetcher.fetch_latest_news(category)

            for item in reversed(news_items):
                if item["id"] not in self.sent_news:
                    await self.post_news(channel, item)
                    self.sent_news.append(item["id"])
                    save_sent_news(self.sent_news)
                    await asyncio.sleep(5)  # evitar rate limit

    @check_news.before_loop
    async def before_check_news(self):
        # Agora sim esperamos o bot estar pronto
        await self.wait_until_ready()

    async def post_news(self, channel, item):
        if item["category"] == "linux":
            role_mention = f"<@&{ROLE_LINUX_ID}>" if ROLE_LINUX_ID else "@Linux"
            color = discord.Color.orange()
        else:
            role_mention = f"<@&{ROLE_WINDOWS_ID}>" if ROLE_WINDOWS_ID else "@Windows"
            color = discord.Color.blue()

        embed = discord.Embed(
            title=item["title"],
            url=item["link"],
            description=item["summary"],
            color=color
        )

        if item["image_url"]:
            embed.set_image(url=item["image_url"])

        embed.set_footer(
            text=f"Fonte: {item['category'].capitalize()} | {item['published']}"
        )

        await channel.send(
            content=f"🔔 **Nova notícia para {role_mention}!**",
            embed=embed
        )


bot = NewsBot()

if __name__ == "__main__":
    if not TOKEN:
        print("Erro: DISCORD_TOKEN não configurado no arquivo .env")
    else:
        bot.run(TOKEN)

