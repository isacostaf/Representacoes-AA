# pesquisa.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

palavras_negativas = [
    # verbos normativos (muito fortes)
    "altera", "alterado", "alterada", "alteração",
    "modifica", "modificado", "modificada",
    "revoga", "revogado", "revogada",
    "revogam-se", "fica revogada", "ficam revogadas",
    "passa a vigorar", "vigorar",
    "substitui", "substituído", "substituída",
    "incluir", "incluído", "incluída",
    "excluir", "excluído", "excluída",

    # estrutura de norma jurídica
    "resolve", "resolvem", "resolve-se",
    "dispõe", "dispoe", "disposições",
    "regulamenta", "regulamentado",
    "estabelece", "estabelecido",
    "institui", "instituído",
    "define", "definido",

    # estrutura de artigo (fortíssimo sinal negativo)
    "art.", "artigo", "§", "parágrafo",
    "inciso", "alínea", "caput",

    # linguagem de alteração normativa
    "dá nova redação", "da nova redacao",
    "passa a ter a seguinte redação",
    "fica alterado", "ficam alterados",
    "fica incluído", "ficam incluídos",
    "fica excluído", "ficam excluídos",

    # referência a normas existentes
    "nos termos da", "na forma da lei",
    "decreto", "portaria", "resolução",
    "lei nº", "lei no", "decreto nº", "portaria nº"
]

def pegar_texto(driver):
    paragrafos = driver.find_elements(By.CLASS_NAME, "dou-paragraph")
    return " ".join([p.text for p in paragrafos]).lower()

def verificar_palavras(texto, palavras, palavras_negativas):
    resultado_pos = {}
    resultado_neg = {}

    for p in palavras:
        resultado_pos[p] = p.lower() in texto

    for p in palavras_negativas:
        resultado_neg[p] = p.lower() in texto

    return resultado_pos, resultado_neg

def analisar_links(url_busca, palavras, status=None, progress=None):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    resumo = []
    detalhes = []
    try:
        if status: status.markdown("🔎 **Filtrando buscas...**")
        if progress: progress.progress(10)

        driver.get(url_busca)
        driver.implicitly_wait(5)

        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")
        links = [(r.text, r.get_attribute("href")) for r in resultados]
        total_links = len(links)

        if status: status.markdown(f"🌐 **Abrindo resultados... {total_links} encontrados**")
        if progress: progress.progress(20)

        for i, (titulo, link) in enumerate(links):
            if progress:
                progresso = 30 + int((i / total_links) * 60)
                progress.progress(progresso)

            if status:
                status.markdown(
                    f"📊 **Analisando documentos {i+1}/{total_links}**<br><small>{titulo}</small>",
                    unsafe_allow_html=True
                )

            driver.get(link)
            driver.implicitly_wait(5)

            texto = pegar_texto(driver)
            resultado_pos, resultado_neg = verificar_palavras(texto, palavras, palavras_negativas)
            negativas_encontradas = [p for p, v in resultado_neg.items() if v]

            # contador positivas
            encontradas = [p for p, v in resultado_pos.items() if v]
            qtd = len(encontradas)
            total = len(palavras)

            # contador negativas
            encontradas_neg = [p for p, v in resultado_neg.items() if v]
            qtd_neg = len(encontradas_neg)
            total_neg = len(palavras_negativas)

            resumo.append({
                "Documento": titulo,
                "PDF": f"[PDF]({link})",
                "Match": f"{qtd}/{total}",
                "Encontradas": ", ".join(encontradas),
                "Match Negativas": f"{qtd_neg}/{total_neg}",
                "Negativas encontradas": ", ".join(negativas_encontradas)
            })

            detalhes.append((titulo, link, resultado_pos, resultado_neg))

        if progress: progress.progress(100)
        if status: status.markdown("✅ **Finalizado!**")

        return resumo

    finally:
        driver.quit()

def gerar_tabela(resumo):
    dados_tabela = []
    for r in resumo:
        link_pdf = r["PDF"].split("(")[1].replace(")", "")
        dados_tabela.append({
            "Documento": r["Documento"],
            "PDF": f'<a href="{link_pdf}" target="_blank">pdf</a>',
            "Match": r["Match"],
            "Palavras encontradas": r["Encontradas"],
            "Match Negativas": r["Match Negativas"],
            "Palavras negativas": r.get("Negativas encontradas", "")
        })

    if not dados_tabela:
        df = pd.DataFrame(columns=["Documento", "Match", "PDF", "Palavras encontradas", "Palavras negativas"])
        df["_qtd"] = pd.Series(dtype="int64")
        styled_df = df.style.hide(axis="columns", subset=["_qtd"])
        return styled_df

    df = pd.DataFrame(dados_tabela)

    # quantidade de matches
    df["_qtd"] = df["Match"].apply(lambda x: int(x.split("/")[0]))
    df["_qtd_total"] = df["Match"].apply(lambda x: int(x.split("/")[1]))

    df["_qtdn"] = df["Match Negativas"].apply(lambda x: int(x.split("/")[0]))
    df["_qtdn_total"] = df["Match Negativas"].apply(lambda x: int(x.split("/")[1]))


    # SCORE (pode ajustar pesos depois)
    df["_score"] = (
        df["_qtd"] * 2.0     # positivo pesa mais
        - df["_qtdn"] * 2.5  # negativo pesa mais ainda
    )

    def destacar_linha(row):

        score = row["_score"]

        # 🟢 alta chance de representação
        if score >= 3:
            return ["background-color: #e6f4ea"] * len(row)

        # 🟡 zona de incerteza (pode ser ou não)
        if 0 < score < 3:
            return ["background-color: #fff9c4"] * len(row)

        # ⚪ neutro / não parece representação
        return [""] * len(row)

    styled_df = df.style.apply(destacar_linha, axis=1)
    styled_df = styled_df.hide(axis="columns", subset=["_qtd"])
    return styled_df