from deep_translator import GoogleTranslator


def traduzir_texto(texto):
    if not texto:
        return ""

    try:
        tradutor = GoogleTranslator(
            source="auto",
            target="pt"
        )

        return tradutor.translate(texto)

    except Exception as erro:
        print(f"❌ Erro ao traduzir: {erro}")

        return texto