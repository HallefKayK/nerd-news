import os

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv


from news.rss import buscar_noticia_mais_recente, buscar_noticias
from news.embed import criar_embed_noticia
from database import criar_tabela
from database import criar_tabela, noticia_existe, salvar_noticia

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1182446203212943441
NEWS_CHANNEL_ID = os.getenv("NEWS_CHANNEL_ID")

if not NEWS_CHANNEL_ID:
    raise RuntimeError(
        "NEWS_CHANNEL_ID não encontrado no arquivo .env"
    )

NEWS_CHANNEL_ID = int(NEWS_CHANNEL_ID)

intents = discord.Intents.default()
intents.message_content = True


class NerdNews(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)


bot = NerdNews()


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    if not verificar_noticias_automaticamente.is_running():
        verificar_noticias_automaticamente.start()


@bot.tree.command(name="ping", description="Verifica se o Nerd News está funcionando.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(
    name="ultimanoticia",
    description="Mostra a notícia mais recente de Games."
)
async def ultima_noticia(interaction: discord.Interaction):

    noticia = buscar_noticia_mais_recente()

    if noticia is None:
        await interaction.response.send_message(
            "❌ Não encontrei nenhuma notícia."
        )
        return

    if noticia_existe(noticia["link"]):
        await interaction.response.send_message(
            "⏭️ Essa notícia já foi publicada anteriormente."
        )
        return

    embed = criar_embed_noticia(
        noticia,
        categoria="Games",
        fonte="GameSpot"
    )

    await interaction.response.send_message(
        embed=embed
    )

    salvar_noticia(
        noticia,
        fonte="GameSpot",
        categoria="Games"
    )
    
async def noticia(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎮 NOVO UPDATE DE SEA OF THIEVES",
        description=(
            "A Rare anunciou uma nova atualização trazendo "
            "novidades e mudanças para os jogadores."
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎮 Categoria",
        value="Games",
        inline=True
    )

    embed.add_field(
        name="📰 Fonte",
        value="Sea of Thieves",
        inline=True
    )

    embed.add_field(
        name="🔗 Notícia completa",
        value="[Clique aqui para ler](https://www.seaofthieves.com/news)",
        inline=False
    )

    embed.set_footer(
        text="🤖 Nerd News • Notícias do mundo nerd"
    )

    await interaction.response.send_message(embed=embed)

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN não encontrado no arquivo .env")

criar_tabela()

async def verificar_noticias():
    canal = bot.get_channel(NEWS_CHANNEL_ID)

    if canal is None:
        print("❌ Canal de notícias não encontrado.")
        return

    noticias = buscar_noticias()

    for noticia in reversed(noticias):

        if noticia_existe(noticia["link"]):
            continue

        embed = criar_embed_noticia(
            noticia,
            categoria="Games",
            fonte="GameSpot"
        )

        await canal.send(embed=embed)

        salvar_noticia(
            noticia,
            fonte="GameSpot",
            categoria="Games"
        )

        print(f"📰 Notícia publicada: {noticia['titulo']}")

@tasks.loop(seconds=30)
async def verificar_noticias_automaticamente():
    try:
        await verificar_noticias()

    except Exception as erro:
        print(f"❌ Erro ao verificar notícias: {erro}")


bot.run(TOKEN)