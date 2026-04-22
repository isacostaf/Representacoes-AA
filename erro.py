from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def csv_vazio(caminho_csv: str = "relatorio.csv") -> bool:
	caminho = Path(caminho_csv)

	if not caminho.exists() or caminho.stat().st_size == 0:
		return True

	try:
		df = pd.read_csv(caminho)
	except (EmptyDataError, ParserError):
		return True

	return df.empty or len(df.columns) == 0
