import os

from news.similarity import encontrar_noticia_semelhante
import discord

from discord.ext import commands, tasks
from dotenv import load_dotenv
from database import (
    buscar_noticias_publicadas,
    criar_tabela,
    noticia_existe,
    salvar_noticia,
)
from news.embed import criar_embed_noticia
from news.rss import buscar_noticia_mais_recente, buscar_noticias_de_todas_as_fontes
from news.similarity import encontrar_noticia_semelhante

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1182446203212943441

GAMES_CHANNEL_ID = os.getenv("GAMES_CHANNEL_ID")
TECH_CHANNEL_ID = os.getenv("TECH_CHANNEL_ID")


if not GAMES_CHANNEL_ID:
    raise RuntimeError(
        "GAMES_CHANNEL_ID não encontrado no arquivo .env"
    )

if not TECH_CHANNEL_ID:
    raise RuntimeError(
        "TECH_CHANNEL_ID não encontrado no arquivo .env"
    )


GAMES_CHANNEL_ID = int(GAMES_CHANNEL_ID)
TECH_CHANNEL_ID = int(TECH_CHANNEL_ID)


CANAIS_NOTICIAS = {
    "games": GAMES_CHANNEL_ID,
    "tecnologia": TECH_CHANNEL_ID
}


NEWS_CHECK_INTERVAL_MINUTES = int(
    os.getenv("NEWS_CHECK_INTERVAL_MINUTES", "5")
)
if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN não encontrado no arquivo .env"
    )

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

    noticias_publicadas = buscar_noticias_publicadas()
    semelhante = encontrar_noticia_semelhante(
        noticia["titulo"],
        noticias_publicadas
    )

    if semelhante is not None:
        await interaction.response.send_message(
            "⏭️ Encontrei uma notícia parecida já publicada anteriormente."
        )
        return

    embed = criar_embed_noticia(
        noticia,
        categoria=noticia.get("categoria", "Games"),
        fonte=noticia.get("fonte", "GameSpot")
    )

    await interaction.response.send_message(
        embed=embed
    )

    salvar_noticia(
        noticia,
        fonte=noticia.get("fonte", "GameSpot"),
        categoria=noticia.get("categoria", "Games")
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

    noticias = buscar_noticias_de_todas_as_fontes()
    noticias_publicadas = buscar_noticias_publicadas()
    print(f"📰 RSS: {len(noticias)} notícias encontradas.")

    for noticia in reversed(noticias):

        try:

            print(f"🔎 Verificando: {noticia['titulo']}")
            if noticia_existe(noticia["link"]):
                print(f"⏭️ Já publicada: {noticia['titulo']}")
                continue    

            semelhante = encontrar_noticia_semelhante(
                noticia["titulo"],
                noticias_publicadas
            )

            if semelhante is not None:
                print(f"⏭️ Parecida com notícia já publicada: {noticia['titulo']}")
                continue

            embed = criar_embed_noticia(
                noticia,
                categoria=noticia["categoria"],
                fonte=noticia["fonte"]
            )
            

            await canal.send(embed=embed)

            salvar_noticia(
                noticia,
                fonte=noticia["fonte"],
                categoria=noticia["categoria"]
            )

            noticias_publicadas.append(noticia)

            print(f"📰 Notícia publicada: {noticia['titulo']}")

        except Exception as erro:

            print(
                f"❌ Erro ao publicar notícia: "
                f"{noticia.get('titulo', 'Sem título')}"
            )

            print(f"Detalhes do erro: {erro}")

@tasks.loop(minutes=NEWS_CHECK_INTERVAL_MINUTES)
async def verificar_noticias_automaticamente():

    try:
        await verificar_noticias()

    except Exception as erro:
        print(f"❌ Erro no sistema de notícias: {erro}")


bot.run(TOKEN)
