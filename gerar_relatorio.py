import pandas as pd

def gerar_csv_relatorio(resumo, caminho_saida="relatorio.csv"):
    df = pd.DataFrame(resumo)

    if df.empty:
        df.to_csv(caminho_saida, index=False, encoding="utf-8")
        return

    # remove markdown da coluna PDF
    if "PDF" in df.columns:
        df["PDF"] = (
            df["PDF"]
            .astype(str)
            .str.extract(r'\((.*?)\)', expand=False)
            .fillna(df["PDF"])
        )

    # garante que Score é numérico
    if "Score" in df.columns:
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce").fillna(0)
    else:
        df["Score"] = 0

    # 🔥 (opcional) criar métricas auxiliares com base no que você já tem
    df["_qtd_pos"] = df["Palavras positivas"].apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) and x else 0
    )

    df["_qtd_neg"] = df["Palavras negativas"].apply(
        lambda x: len(x.split(", ")) if isinstance(x, str) and x else 0
    )

    # 🔥 score final (mais consistente com seu sistema)
    df["_score_final"] = (
        df["Score"] * 1.0
        + df["_qtd_pos"] * 1.5
        - df["_qtd_neg"] * 2.0
    )

    # filtra apenas os mais relevantes
    filtro = df["_score_final"] > 0

    # ordena por relevância
    df_filtrado = df[filtro].sort_values(by="_score_final", ascending=False)

    # gera CSV final
    df_filtrado.to_csv(
        caminho_saida,
        columns=["Documento", "PDF", "Score"],
        index=False,
        encoding="utf-8"
    )