import pandas as pd

def gerar_csv_relatorio(resumo):
    df = pd.DataFrame(resumo)

    if df.empty:
        return ""

    # remove markdown da coluna PDF
    if "PDF" in df.columns:
        df["PDF"] = (
            df["PDF"]
            .astype(str)
            .str.extract(r'\((.*?)\)', expand=False)
            .fillna(df["PDF"])
        )

    # garante Score
    df["Score"] = df["Score Base"] + df["Score Representação"]

    # classificação
    def classificar(row):
        score_base = row["Score Base"]
        score_rep = row["Score Representação"]

        # 🟢 Alta chance → representação detectada
        if score_rep >= 8:
            return "Alta chance"

        # 🟡 Talvez → sem representação, mas score alto
        elif score_base > 2:
            return "Talvez"

        # 🔴 Baixa chance
        else:
            return "Baixa chance"

    df["Classificação"] = df.apply(classificar, axis=1)
    
    # ordena
    df = df.sort_values(by="Score", ascending=False)

    # 🔥 gera CSV em string (não salva arquivo)
    csv = df[["Documento", "PDF", "Classificação"]].to_csv(
        index=False,
        encoding="utf-8"
    )

    return csv