FILTROS = {
    "games": {
        "ativo": True,

        "palavras_chave": [
            "Sea of Thieves",
            "GTA",
            "Grand Theft Auto",
            "Minecraft",
            "Valorant",
            "Fortnite",
            "Call of Duty",
            "Elden Ring",
            "FromSoftware",
            "PlayStation",
            "Xbox",
            "Nintendo",
            "Steam"
        ]
    }
}


def noticia_interessa(noticia, categoria):

    configuracao = FILTROS.get(categoria)

    # Categoria sem filtro = aceita normalmente
    if not configuracao:
        return True

    # Filtro desativado = aceita tudo
    if not configuracao.get("ativo", False):
        return True

    palavras = configuracao.get(
        "palavras_chave",
        []
    )

    # Sem palavras cadastradas = aceita tudo
    if not palavras:
        return True

    texto = (
        noticia.get("titulo_original", "")
        + " "
        + noticia.get("descricao", "")
    ).lower()

    for palavra in palavras:

        if palavra.lower() in texto:
            return True

    return False

def noticia_valida(noticia):
    titulo = noticia.get("titulo", "").lower()
    link = noticia.get("link", "")

    if not titulo:
        return False

    erros = [
        "error 500",
        "server error",
        "404 not found",
        "access denied",
        "page not found"
    ]

    for erro in erros:
        if erro in titulo:
            return False

    if not link.startswith("http"):
        return False

    return True
    return True

def classificar_categoria(noticia, categoria_original):
    link = noticia.get("link", "").lower()

    if "/hardware/" in link:
        return "tecnologia"

    if "/software/" in link:
        return "tecnologia"

    if "/computing/" in link:
        return "tecnologia"

    if "/games/" in link:
        return "games"

    if "/gaming/" in link:
        return "games"

    if "/reviews/" in link:
        return categoria_original

    return categoria_original