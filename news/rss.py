import re
from datetime import datetime, timezone
import os

import feedparser

from news.filter import (
    noticia_interessa,
    noticia_valida,
    classificar_categoria
)
from news.translator import traduzir_texto
from sources.config import FONTES

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

def noticia_eh_recente(entrada):
    limite_horas = int(
        os.getenv("MAX_NEWS_AGE_HOURS", "6")
    )

    data_publicacao = entrada.get("published_parsed")

    if not data_publicacao:
        return True

    data_publicacao = datetime(
        *data_publicacao[:6],
        tzinfo=timezone.utc
    )

    agora = datetime.now(timezone.utc)

    idade = agora - data_publicacao

    return idade.total_seconds() <= limite_horas * 3600


def buscar_noticias(url):

    limite = 10

    feed = feedparser.parse(url)

    noticias = []

    for entrada in feed.entries[:limite]:
        if not noticia_eh_recente(entrada):
            continue

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

def buscar_noticias_de_todas_as_fontes():

    todas_as_noticias = []

    for categoria, fontes in FONTES.items():

        for nome_fonte, configuracao in fontes.items():

            if not configuracao["ativo"]:
                continue

            url = configuracao["url"]

            print(
                f"🔎 Buscando notícias: "
                f"{nome_fonte} ({categoria})"
            )

            try:

                noticias = buscar_noticias(url)

                noticias_filtradas = []

                for noticia in noticias:

                    noticia["categoria"] = categoria
                    noticia["fonte"] = nome_fonte

                    if not noticia_valida(noticia):
                        print(
                            f"❌ Entrada ignorada: "
                            f"{noticia['titulo', 'Sem título']}"
                        )
                        continue
                    categoria_real = classificar_categoria(
                        noticia,
                        categoria
                    )

                    noticia["categoria"] = categoria_real
                    noticia["fonte"] = nome_fonte

            except Exception as erro:

                print(
                    f"❌ Erro ao consultar "
                    f"{nome_fonte}: {erro}"
                )

    return todas_as_noticias

def buscar_noticia_mais_recente():
    noticias = buscar_noticias_de_todas_as_fontes()

    if not noticias:
        return None

    return noticias[0]


if __name__ == "__main__":

    noticias = buscar_noticias_de_todas_as_fontes()

    print(f"\nEncontradas {len(noticias)} notícias.\n")

    for noticia in noticias:
        print("\n----------------------------")
        print(f"Título: {noticia['titulo']}")
        print(f"Link: {noticia['link']}")
        print(f"Imagem: {noticia['imagem']}")
        print(f"Data: {noticia['data']}")

    
