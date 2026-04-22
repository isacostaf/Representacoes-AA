from __future__ import annotations

import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path
import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from dotenv import load_dotenv
load_dotenv()

def _listar_destinatarios() -> list[str]:
	raw = os.getenv("EMAIL_TO", "")
	if not raw:
		return []

	valores = raw.replace(";", ",").split(",")
	return [v.strip() for v in valores if v.strip()]

def _carregar_representacoes(caminho_csv: str) -> tuple[list[str], list[str]]:
	caminho = Path(caminho_csv)
	if not caminho.exists():
		return [], []

	try:
		df = pd.read_csv(caminho)
	except (EmptyDataError, ParserError):
		return [], []

	if df.empty or "Documento" not in df.columns:
		return [], []

	df["Documento"] = df["Documento"].astype(str).str.strip()
	df = df[df["Documento"] != ""]
	if df.empty:
		return [], []

	if "Classificação" in df.columns:
		df["Classificação"] = df["Classificação"].astype(str).str.strip().str.lower()
		alta = [
			nome
			for nome in df.loc[df["Classificação"] == "alta chance", "Documento"].dropna().tolist()
			if str(nome).strip()
		]
		talvez = [
			nome
			for nome in df.loc[df["Classificação"] == "talvez", "Documento"].dropna().tolist()
			if str(nome).strip()
		]
		return alta, talvez

def _montar_corpo_email(alta_chance: list[str], talvez: list[str]) -> str:
	tem_representacoes = bool(alta_chance or talvez)
	if not tem_representacoes:
		return (
			"Prezados,\n\n"
			"Informamos que, na consulta realizada hoje, nao foram identificadas representacoes.\n\n"
			"Atenciosamente,\n"
			"Equipe de Monitoramento"
		)

	lista_alta = "\n".join(f"- {nome}" for nome in alta_chance) if alta_chance else "- Nenhum arquivo nesta categoria"
	lista_talvez = "\n".join(f"- {nome}" for nome in talvez) if talvez else "- Nenhum arquivo nesta categoria"

	return (
		"Prezados,\n\n"
		"Informamos que foram identificadas representacoes na consulta realizada hoje.\n"
		"Seguem abaixo os documentos localizados:\n\n"
		"Arquivos de Alta chance:\n"
		f"{lista_alta}\n\n"
		"Arquivos de Talvez:\n"
		f"{lista_talvez}\n\n"
		"Encaminhamos em anexo o relatorio CSV e os arquivos PDF correspondentes.\n\n"
		"Atenciosamente,\n"
		"Equipe de Monitoramento"
	)


def _adicionar_anexo(msg: EmailMessage, arquivo: Path) -> None:
	conteudo = arquivo.read_bytes()
	if arquivo.suffix.lower() == ".pdf":
		maintype, subtype = "application", "pdf"
	elif arquivo.suffix.lower() == ".csv":
		maintype, subtype = "text", "csv"
	else:
		maintype, subtype = "application", "octet-stream"

	msg.add_attachment(conteudo, maintype=maintype, subtype=subtype, filename=arquivo.name)


def _listar_pdfs_para_anexo(pasta_pdfs: str) -> list[Path]:
	pasta = Path(pasta_pdfs)
	if not pasta.exists():
		return []

	return sorted(
		[arquivo for arquivo in pasta.rglob("*.pdf") if arquivo.is_file()],
		key=lambda p: (str(p.parent), p.name.lower()),
	)


def enviar_email(
	caminho_csv: str = "relatorio.csv",
	pasta_pdfs: str = "pdfs",
) -> dict:
	smtp_host = os.getenv("SMTP_HOST")
	smtp_port = int(os.getenv("SMTP_PORT"))
	smtp_usuario = os.getenv("SMTP_USER")
	smtp_senha = os.getenv("SMTP_PASSWORD")
	email_remetente = os.getenv("EMAIL_FROM", smtp_usuario)
	destinatarios = _listar_destinatarios()

	nomes_alta_chance, nomes_talvez = _carregar_representacoes(caminho_csv)
	pdfs_para_anexo = _listar_pdfs_para_anexo(pasta_pdfs)

	msg = EmailMessage()
	msg["From"] = email_remetente
	msg["To"] = ", ".join(destinatarios)
	msg["Subject"] = f"Representacoes {date.today().strftime('%d/%m/%Y')}"
	msg.set_content(_montar_corpo_email(nomes_alta_chance, nomes_talvez))

	csv_path = Path(caminho_csv)
	if csv_path.exists():
		_adicionar_anexo(msg, csv_path)

	for pdf in pdfs_para_anexo:
		_adicionar_anexo(msg, pdf)

	if smtp_port == 465:
		with smtplib.SMTP_SSL(smtp_host, smtp_port) as servidor:
			servidor.login(smtp_usuario, smtp_senha)
			servidor.send_message(msg)
	else:
		with smtplib.SMTP(smtp_host, smtp_port) as servidor:
			servidor.ehlo()
			servidor.starttls()
			servidor.ehlo()
			servidor.login(smtp_usuario, smtp_senha)
			servidor.send_message(msg)