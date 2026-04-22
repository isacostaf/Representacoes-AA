import re
import base64
from html import unescape
import pandas as pd
from pandas.errors import EmptyDataError, ParserError

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import io
import zipfile


REGEX_HREF = re.compile(r'href=["\']([^"\']+)["\']', flags=re.IGNORECASE)

def criar_zip(pasta: str) -> bytes:
    buffer = io.BytesIO()
    caminho = Path(pasta)

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in caminho.rglob("*.pdf"):
            zipf.write(arquivo, arcname=arquivo.name)

    buffer.seek(0)
    return buffer.getvalue()


def renomear(texto: str) -> str:
    REGEX_NOME = re.compile(r'[\\/:*?"<>|]+')
    return REGEX_NOME.sub(" ", str(texto or "documento")).strip().replace(" ", "_") or "documento"


def criar_driver():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver

def imprimir_pagina_em_pdf(driver, url: str, caminho_saida: Path, timeout: int = 30) -> None:
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )

    pdf_data = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "preferCSSPageSize": True,
        },
    )
    caminho_saida.write_bytes(base64.b64decode(pdf_data["data"]))


def limpar_pasta_pdf(pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    for arquivo in pasta.glob("*.pdf"):
        try:
            arquivo.unlink()
        except:
            pass


def obter_pasta_classificacao(classificacao: str, pasta_base: Path) -> Path | None:
    valor = str(classificacao).strip().lower()

    if valor == "talvez":
        return pasta_base / "talvez"
    elif valor == "alta chance":
        return pasta_base / "alta_chance"

    return None


def extrair_url_pdf(valor_pdf: str) -> str:
    valor = unescape(str(valor_pdf or "").strip())
    if not valor:
        return ""

    if valor.lower().startswith(("http://", "https://")):
        return valor

    match = REGEX_HREF.search(valor)
    if match:
        return match.group(1).strip()

    return ""


def baixar_pdf(caminho_csv: str = "relatorio.csv", pasta_saida: str = "pdfs") -> dict:
    
    df = pd.read_csv(caminho_csv)

    pasta_base = Path(pasta_saida)
    pasta_talvez = pasta_base / "talvez"
    pasta_alta = pasta_base / "alta_chance"

    limpar_pasta_pdf(pasta_talvez)
    limpar_pasta_pdf(pasta_alta)

    driver = criar_driver()

    try:
        for linha in df[["Documento", "PDF", "Classificação"]].fillna("").to_dict("records"):
            nome = renomear(linha["Documento"])
            url = extrair_url_pdf(linha["PDF"])
            classificacao = linha["Classificação"]

            pasta_destino = obter_pasta_classificacao(classificacao, pasta_base)

            if pasta_destino is None or not url:
                continue

            try:
                pasta_destino.mkdir(parents=True, exist_ok=True)

                caminho = pasta_destino / f"{nome}.pdf"
                i = 1
                while caminho.exists():
                    caminho = pasta_destino / f"{nome}_{i}.pdf"
                    i += 1

                imprimir_pagina_em_pdf(driver, url, caminho)

            except Exception:
                pass

    finally:
        driver.quit()
