import discord


def limitar_texto(texto, limite):
    if not texto:
        return ""

    if len(texto) <= limite:
        return texto

    return texto[:limite - 3] + "..."


def criar_embed_noticia(noticia, categoria="Games", fonte="GameSpot"):

    titulo = limitar_texto(
        noticia.get("titulo", "Sem título"),
        256
    )

    descricao = limitar_texto(
        noticia.get("descricao", ""),
        1000
    )

    embed = discord.Embed(
        title=f"🎮 {titulo}",
        url=noticia.get("link", ""),
        description=descricao,
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📂 Categoria",
        value=limitar_texto(categoria, 1024),
        inline=True
    )

    embed.add_field(
        name="📰 Fonte",
        value=limitar_texto(fonte, 1024),
        inline=True
    )

    if noticia.get("data"):
        embed.add_field(
            name="📅 Publicado em",
            value=limitar_texto(noticia["data"], 1024),
            inline=False
        )

    if noticia.get("imagem"):
        embed.set_image(
            url=noticia["imagem"]
        )

    embed.set_footer(
        text="🤖 Nerd News • Notícias do mundo nerd"
    )

    return embed