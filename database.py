import sqlite3


DATABASE_NAME = "nerd_news.db"


def conectar():
    return sqlite3.connect(DATABASE_NAME)


def criar_tabela():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            fonte TEXT NOT NULL,
            categoria TEXT NOT NULL,
            data_publicacao TEXT
        )
    """)

    conexao.commit()
    conexao.close()


def noticia_existe(url):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id FROM noticias WHERE url = ?",
        (url,)
    )

    resultado = cursor.fetchone()

    conexao.close()

    return resultado is not None


def salvar_noticia(noticia, fonte, categoria):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO noticias (
            url,
            titulo,
            fonte,
            categoria,
            data_publicacao
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        noticia["link"],
        noticia["titulo"],
        fonte,
        categoria,
        noticia.get("data", "")
    ))

    conexao.commit()
    conexao.close()