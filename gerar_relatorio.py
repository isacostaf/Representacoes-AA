import pandas as pd

def gerar_csv_relatorio(resumo, caminho_saida="relatorio.csv"):
    df = pd.DataFrame(resumo)

    if df.empty:
        df.to_csv(caminho_saida, index=False, encoding="utf-8")
        return

    # retira o markdown da coluna PDF
    if "PDF" in df.columns:
        df["PDF"] = (df["PDF"].astype(str).str.extract(r'\((.*?)\)', expand=False).fillna(df["PDF"]))

    # garante Score
    df["Score"] = df["Score Base"] + df["Score Representação"]
    
    # classificação
    def classificar(score):
        if score >= 5:
            return "Alta chance"
        elif score > 0:
            return "Talvez"
        else:
            return "Baixa chance"

    df["Classificação"] = df["Score"].apply(classificar)

    # filtra por score positivo
    filtro = df["Score"] > 0

    # gera o CSV
    df[filtro].drop(columns=["Score"], errors="ignore").to_csv(
        caminho_saida,
        columns=["Documento", "PDF", "Classificação"],
        index=False,
        encoding="utf-8"
    )
def gerar_csv_relatorio_downloud(resumo):
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
    df = df.sort_values(by=["Score Base", "Score Representação"], ascending=False)

    # 🔥 gera CSV em string (não salva arquivo)
    csv = df.drop(columns=["Score"], errors="ignore")[["Documento", "PDF", "Classificação"]].to_csv(
        index=False,
        encoding="utf-8"
    )

    return csv