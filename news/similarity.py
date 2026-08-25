import re


def normalizar_titulo(titulo):

    titulo = titulo.lower()

    titulo = re.sub(
        r"[^\w\s]",
        "",
        titulo
    )

    titulo = re.sub(
        r"\s+",
        " ",
        titulo
    ).strip()

    return titulo

from difflib import SequenceMatcher


def titulos_sao_semelhantes(
    titulo1,
    titulo2,
    limite=0.80
):

    titulo1 = normalizar_titulo(titulo1)
    titulo2 = normalizar_titulo(titulo2)

    semelhanca = SequenceMatcher(
        None,
        titulo1,
        titulo2
    ).ratio()

    return semelhanca >= limite

def encontrar_noticia_semelhante(
    titulo,
    noticias_publicadas,
    limite=0.80
):

    for noticia in noticias_publicadas:

        if titulos_sao_semelhantes(
            titulo,
            noticia["titulo"],
            limite
        ):
            return noticia

    return None

if __name__ == "__main__":

    titulo1 = (
        "Sea of Thieves recebe nova atualização!"
    )

    titulo2 = (
        "Sea of Thieves ganha nova atualização"
    )

    resultado = titulos_sao_semelhantes(
        titulo1,
        titulo2
    )

    print(f"São semelhantes? {resultado}")