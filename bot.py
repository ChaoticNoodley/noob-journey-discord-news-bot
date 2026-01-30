import discord
from discord.ext import tasks, commands
import os
import json
from dotenv import load_dotenv
from news_fetcher import NewsFetcher
import asyncio

# --- CONFIGURAÇÕES DE AMBIENTE ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 3600))

SENT_NEWS_FILE = "sent_news.json"
CONFIG_FILE = "server_config.json"

# --- UTILITÁRIOS DE ARQUIVO ---
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

# --- CLASSE DO BOT ---
class NewsBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix="!", intents=intents, help_command=None)

        self.fetcher = NewsFetcher()
        self.sent_news = load_sent_news()
        self.configs = load_configs()

        self.status_list = [
            "Modificando o Proton",
            "Lendo RSS",
            "Compilando Kernel",
            "Atualizando Windows",
            "Servindo notícias quentinhas ☕"
        ]
        self.status_index = 0

    async def setup_hook(self):
        # Inicia os loops assim que o bot carrega as extensões
        self.check_news.start()
        self.rotate_status.start()

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.user}")
        print(f"📦 Configs carregadas para {len(self.configs)} servidor(es)")

    # LOOP DE STATUS (CORRIGIDO)
    @tasks.loop(seconds=60)
    async def rotate_status(self):
        # ESSENCIAL: Espera a conexão WebSocket estar pronta antes de mudar o status
        await self.wait_until_ready()
        
        try:
            activity = discord.Game(name=self.status_list[self.status_index])
            await self.change_presence(status=discord.Status.online, activity=activity)
            self.status_index = (self.status_index + 1) % len(self.status_list)
        except Exception as e:
            print(f"❌ Erro no rotate_status: {e}")

    # LOOP DE NOTÍCIAS (CORRIGIDO)
    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_news(self):
        await self.wait_until_ready()
        
        for guild_id, config in list(self.configs.items()):
            channel_id = config.get("channel_id")
            if not channel_id:
                continue

            try:
                # Usar fetch_channel garante que pegamos o canal mesmo após reboot
                channel = await self.fetch_channel(channel_id)
            except Exception as e:
                print(f"⚠️ Não consegui acessar o canal {channel_id}: {e}")
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
                        await asyncio.sleep(5) # Delay para evitar Rate Limit

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

        embed.set_footer(text=f"Fonte: {item['category'].capitalize()} | {item['published']}")

        await channel.send(
            content=f"🔔 **Breaking News!** {role_mentions}",
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True)
        )

# Instância única do Bot
bot = NewsBot()

# --- COMANDOS ---

@bot.command()
@commands.has_permissions(administrator=True)
async def setchannel(ctx):
    gid = str(ctx.guild.id)
    bot.configs.setdefault(gid, {})
    bot.configs[gid]["channel_id"] = ctx.channel.id
    bot.configs[gid]["windows"] = True
    bot.configs[gid]["linux"] = True
    save_configs(bot.configs)
    await ctx.send(f"✅ Canal configurado: {ctx.channel.mention}")

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

    gid = str(ctx.guild.id)
    bot.configs.setdefault(gid, {})
    bot.configs[gid].setdefault("roles", {})
    bot.configs[gid]["roles"].setdefault(os_name, [])

    if role.id not in bot.configs[gid]["roles"][os_name]:
        bot.configs[gid]["roles"][os_name].append(role.id)
        save_configs(bot.configs)
        await ctx.send(f"✅ Cargo adicionado para {os_name}: {role.mention}")
    else:
        await ctx.send("⚠️ Esse cargo já está configurado.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removerole(ctx, os_name: str, role: discord.Role):
    gid = str(ctx.guild.id)
    roles = bot.configs.get(gid, {}).get("roles", {}).get(os_name, [])

    if role.id in roles:
        roles.remove(role.id)
        save_configs(bot.configs)
        await ctx.send(f"🗑️ Cargo removido: {role.mention}")
    else:
        await ctx.send("⚠️ Cargo não encontrado.")

@bot.command()
@commands.has_permissions(administrator=True)
async def clearroles(ctx):
    gid = str(ctx.guild.id)
    if gid in bot.configs and "roles" in bot.configs[gid]:
        bot.configs[gid]["roles"] = {}
        save_configs(bot.configs)
        await ctx.send("🧹 Todos os cargos removidos.")
    else:
        await ctx.send("⚠️ Nenhum cargo configurado.")

@bot.command()
async def showroles(ctx):
    config = bot.configs.get(str(ctx.guild.id), {})
    roles = config.get("roles", {})

    if not roles:
        await ctx.send("⚠️ Nenhum cargo configurado.")
        return

    msg = "📌 **Cargos configurados:**\n"
    for os_name, role_ids in roles.items():
        mentions = []
        for rid in role_ids:
            role = ctx.guild.get_role(rid)
            if role:
                mentions.append(role.mention)
        msg += f"**{os_name.capitalize()}**: {' '.join(mentions) if mentions else 'Nenhum'}\n"

    await ctx.send(msg)

@bot.command()
async def say(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def testnews(ctx):
    await ctx.send("🔎 Testando envio de notícias...")
    for cat in ["windows", "linux"]:
        news = bot.fetcher.fetch_latest_news(cat, limit=1)
        if news:
            await bot.post_news(ctx.channel, news[0], str(ctx.guild.id))

@bot.command()
async def helpwinux(ctx):
    embed = discord.Embed(
        title="🤖 Winux-chan Commands",
        description="Bot de notícias sobre Windows & Linux",
        color=discord.Color.purple()
    )

    embed.set_image(
        url="https://imgur.com/zHHSPx9.gif"
    )

    embed.add_field(
        name="📡 Configuração",
        value=
        "`!setchannel` - Define o canal atual\n"
        "`!showconfig` - Mostra a configuração da Winux-chan
        "`!setrole windows @Role` - Adiciona cargo p/ Windows\n"
        "`!setrole linux @Role` - Adiciona cargo p/ Linux\n"
        "`!removerole windows @Role` - Remove cargo\n"
        "`!clearroles` - Limpa todos os cargos\n"
        "`!showroles` - Mostra cargos configurados",
        inline=False
    )

    embed.add_field(
        name="🧪 Outros",
        value=
        "`!testnews` - Testa o envio manual\n"
        "`!say <msg>` - Faz o bot falar",
        inline=False
    )

    embed.set_footer(text="Winux-chan só no Go Drinking")
    await ctx.send(embed=embed)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERRO: DISCORD_TOKEN não encontrado no arquivo .env")
    else:
        bot.run(TOKEN)
