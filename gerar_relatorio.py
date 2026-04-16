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
    df["Score"] = pd.to_numeric(df.get("Score", 0), errors="coerce").fillna(0)

    # classificação baseada no seu padrão visual
    def classificar(score):
        if score >= 5:
            return "Alta chance"
        elif score > 0:
            return "Talvez"
        else:
            return "Baixa chance"

    df["Classificação"] = df["Score"].apply(classificar)

    # ordenar pelos melhores (opcional)
    df = df.sort_values(by="Score", ascending=False)

    # 🔥 CSV FINAL (sem Score)
    df.to_csv(
        caminho_saida,
        columns=["Documento", "PDF", "Classificação"],
        index=False,
        encoding="utf-8"
    )