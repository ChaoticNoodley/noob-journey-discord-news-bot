import discord
from discord.ext import tasks, commands
import os
import json
from dotenv import load_dotenv
from news_fetcher import NewsFetcher
import asyncio

# ENV
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))

SENT_NEWS_FILE = "sent_news.json"
CONFIG_FILE = "server_config.json"


# FILE UTILS

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
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erro ao ler server_config.json. Usando config vazia.")
            return {}
    return {}


def save_configs(configs):
    with open(CONFIG_FILE, "w") as f:
        json.dump(configs, f, indent=4)


# Winux-chan

class NewsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix="!", intents=intents)

        self.fetcher = NewsFetcher()
        self.sent_news = load_sent_news()
        self.configs = load_configs()

    async def setup_hook(self):
        self.check_news.start()

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.user}")
        print("📦 Configs carregadas:", self.configs)

    # LOOP ∞

    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_news(self):
        for guild_id, config in list(self.configs.items()):

            channel_id = config.get("channel_id")
            if not channel_id:
                continue

            try:
                channel = await self.fetch_channel(channel_id)
            except discord.NotFound:
                print(f"❌ Canal {channel_id} não existe. Removendo config.")
                del self.configs[guild_id]
                save_configs(self.configs)
                continue
            except discord.Forbidden:
                print(f"⛔ Sem permissão para acessar canal {channel_id}.")
                continue
            except discord.HTTPException as e:
                print(f"⚠️ Erro HTTP ao buscar canal {channel_id}: {e}")
                continue

            categories = []
            if config.get("windows"):
                categories.append("windows")
            if config.get("linux"):
                categories.append("linux")

            for category in categories:
                try:
                    news_items = self.fetcher.fetch_latest_news(category)
                except Exception as e:
                    print(f"Erro ao buscar notícias ({category}): {e}")
                    continue

                for item in reversed(news_items):
                    if item["id"] not in self.sent_news:
                        await self.post_news(channel, item, guild_id)
                        self.sent_news.append(item["id"])
                        save_sent_news(self.sent_news)
                        await asyncio.sleep(5)

    # SEND NEWS

    async def post_news(self, channel, item, guild_id):
        config = self.configs.get(str(guild_id), {})
        roles_cfg = config.get("roles", {})

        role_ids = roles_cfg.get(item["category"], [])

        if isinstance(role_ids, int):
            role_ids = [role_ids]

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

        embed.set_footer(text=f"Fonte: {item['category'].capitalize()} | {item['published']}")

        await channel.send(
            content=f"🔔 **Breaking News!** {role_mentions}",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )


bot = NewsBot()

# COMMANDS#

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    guild_id = str(ctx.guild.id)

    if guild_id not in bot.configs:
        bot.configs[guild_id] = {}

    bot.configs[guild_id]["channel_id"] = ctx.channel.id
    bot.configs[guild_id]["windows"] = True
    bot.configs[guild_id]["linux"] = True

    save_configs(bot.configs)
    await ctx.send(f"✅ Canal configurado para notícias: {ctx.channel.mention}")

@bot.command()
async def showconfig(ctx):
    guild_id = str(ctx.guild.id)
    config = bot.configs.get(guild_id)

    if not config:
        await ctx.send("⚠️ Este servidor ainda não foi configurado. Use `!setchannel`.")
        return

    channel = bot.get_channel(config["channel_id"])
    channel_name = channel.mention if channel else "Canal inválido"

    await ctx.send(
        f"📡 **Configuração atual:**\n"
        f"Canal: {channel_name}\n"
        f"Windows: {config.get('windows')}\n"
        f"Linux: {config.get('linux')}"
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def setrole(ctx, os_name: str, role: discord.Role):
    os_name = os_name.lower()

    if os_name not in ["windows", "linux"]:
        await ctx.send("Use: `!setrole windows @Role` ou `!setrole linux @Role`")
        return

    guild_id = str(ctx.guild.id)

    if guild_id not in bot.configs:
        bot.configs[guild_id] = {}

    if "roles" not in bot.configs[guild_id]:
        bot.configs[guild_id]["roles"] = {}

    if os_name not in bot.configs[guild_id]["roles"]:
        bot.configs[guild_id]["roles"][os_name] = []

    if role.id in bot.configs[guild_id]["roles"][os_name]:
        await ctx.send(f"⚠️ {role.mention} já configurado para {os_name}.")
        return

    bot.configs[guild_id]["roles"][os_name].append(role.id)
    save_configs(bot.configs)

    await ctx.send(f"✅ Cargo adicionado para **{os_name}**: {role.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def removerole(ctx, os_name: str, role: discord.Role):
    os_name = os_name.lower()

    if os_name not in ["windows", "linux"]:
        await ctx.send("Use: `!removerole windows @Role` ou `!removerole linux @Role`")
        return

    guild_id = str(ctx.guild.id)
    config = bot.configs.get(guild_id, {})
    roles = config.get("roles", {})

    if os_name not in roles:
        await ctx.send(f"⚠️ Nenhum cargo configurado para {os_name}.")
        return

    if role.id not in roles[os_name]:
        await ctx.send(f"⚠️ {role.mention} não está configurado para {os_name}.")
        return

    roles[os_name].remove(role.id)
    save_configs(bot.configs)

    await ctx.send(f"🗑️ Cargo removido de **{os_name}**: {role.mention}")


@bot.command()
@commands.has_permissions(administrator=True)
async def clearroles(ctx, os_name: str):
    os_name = os_name.lower()

    if os_name not in ["windows", "linux"]:
        await ctx.send("Use: `!clearroles windows` ou `!clearroles linux`")
        return

    guild_id = str(ctx.guild.id)

    if guild_id not in bot.configs:
        await ctx.send("Servidor não configurado.")
        return

    if "roles" not in bot.configs[guild_id]:
        await ctx.send("Nenhum cargo configurado ainda.")
        return

    bot.configs[guild_id]["roles"][os_name] = []
    save_configs(bot.configs)

    await ctx.send(f"🧹 Todos os cargos de **{os_name}** foram removidos.")


@bot.command()
async def showroles(ctx):
    config = bot.configs.get(str(ctx.guild.id), {})
    roles = config.get("roles", {})

    if not roles:
        await ctx.send("⚠️ Nenhum cargo configurado ainda.")
        return

    msg = "📌 **Cargos configurados:**\n"

    for os_name, role_ids in roles.items():
        if isinstance(role_ids, int):
            role_ids = [role_ids]

        role_mentions = []
        for rid in role_ids:
            role = ctx.guild.get_role(rid)
            if role:
                role_mentions.append(role.mention)

        msg += f"{os_name}: {' '.join(role_mentions)}\n"

    await ctx.send(msg)


@bot.command()
@commands.has_permissions(administrator=True)
async def testnews(ctx):
    await ctx.send("🔎 Testando envio de notícias...")

    config = bot.configs.get(str(ctx.guild.id))
    if not config:
        await ctx.send("Servidor não configurado. Use !setchannel")
        return

    try:
        channel = await bot.fetch_channel(config["channel_id"])
    except Exception:
        await ctx.send("Erro ao acessar o canal configurado.")
        return

    for category in ["windows", "linux"]:
        news = bot.fetcher.fetch_latest_news(category, limit=1)
        if news:
            await bot.post_news(channel, news[0], str(ctx.guild.id))
        else:
            await ctx.send(f"Nenhuma notícia encontrada para {category}")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)


# HELLO WORLD?

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN não configurado.")
    else:
        bot.run(TOKEN)
