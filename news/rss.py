import re

import feedparser

from news.translator import traduzir_texto

RSS_URL = "https://www.gamespot.com/feeds/mashup/"


def limpar_html(texto):
    texto = re.sub(r"<[^>]+>", "", texto)
    return texto.strip()


def extrair_imagem(noticia):
    imagem = None

    if hasattr(noticia, "media_content"):
        if noticia.media_content:
            imagem = noticia.media_content[0].get("url")

    if not imagem and hasattr(noticia, "media_thumbnail"):
        if noticia.media_thumbnail:
            imagem = noticia.media_thumbnail[0].get("url")

    return imagem


def buscar_noticias(limite=10):
    feed = feedparser.parse(RSS_URL)

    noticias = []

    for entrada in feed.entries[:limite]:

        titulo_original = entrada.get(
            "title",
            "Sem título"
        )

        descricao_original = limpar_html(
            entrada.get("description", "")
        )

        descricao_para_traduzir = descricao_original[:3000]

        noticia = {
            "titulo": traduzir_texto(titulo_original),
            "titulo_original": titulo_original,
            "link": entrada.get("link", ""),
            "descricao": traduzir_texto(
                descricao_para_traduzir
            ),
            "imagem": extrair_imagem(entrada),
            "data": entrada.get("published", ""),
        }

        noticias.append(noticia)

    return noticias


def buscar_noticia_mais_recente():
    noticias = buscar_noticias(1)

    if not noticias:
        return None

    return noticias[0]


if __name__ == "__main__":
    noticias = buscar_noticias()

    print(f"Encontradas {len(noticias)} notícias.")

    for noticia in noticias:
        print("\n----------------------------")
        print(f"Título: {noticia['titulo']}")
        print(f"Link: {noticia['link']}")
        print(f"Imagem: {noticia['imagem']}")
        print(f"Data: {noticia['data']}")