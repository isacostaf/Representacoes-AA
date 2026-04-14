import pandas as pd

def gerar_csv_relatorio(resumo, caminho_saida="relatorio.csv"):
	df = pd.DataFrame(resumo)

	# retira o markdown da coluna PDF
	df["PDF"] = df["PDF"].str.extract(r'\((.*?)\)', expand=False)

	# separa a coluna Match em duas colunas: Match_Encontradas e Match_Total
	match = df["Match"].str.split("/", n=1, expand=True)
	df["Match_Encontradas"] = pd.to_numeric(match[0], errors="coerce")
	df["Match_Total"] = pd.to_numeric(match[1], errors="coerce")

	# filtra a coluna Match_Encontradas
	filtro = (df["Match_Encontradas"].fillna(0) > 0)

	# gera o arquivo csv 
	df[filtro].to_csv(caminho_saida, columns=["Documento", "PDF"], index=False, encoding="utf-8")
