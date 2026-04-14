# analise.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re

# =========================
# PESOS INTELIGENTES
# =========================
palavras_bloqueio = [
    "conportos", "CONPORTOS"
]

pesos_positivos = {
    "designa": 5,
    "designar": 5,
    "designados": 5,
    "nomeia": 5,
    "indicados": 5,
    "para compor": 6,
    "ficam designados": 7,

    "membro": 2,
    "membros": 2,
    "representante": 3,
    "representantes": 3,
    "titular": 2,
    "suplente": 2,

    "presidente": 1,
    "coordenador": 1,
    "relator": 1,
}

pesos_negativos = {
    "art.": 6,
    "artigo": 6,
    "§": 6,
    "inciso": 6,

    "altera": 4,
    "revoga": 4,
    "regulamenta": 3,

    "portaria": 1,
    "decreto": 1,
}

# =========================
# PALAVRAS NEGATIVAS
# =========================

palavras_negativas = [
    "altera", "alterado", "alterada", "alteração",
    "modifica", "modificado", "modificada",
    "revoga", "revogado", "revogada",
    "revogam-se", "fica revogada", "ficam revogadas",
    "passa a vigorar", "vigorar",
    "substitui", "substituído", "substituída",
    "incluir", "incluído", "incluída",
    "excluir", "excluído", "excluída",

    "resolve", "resolvem", "resolve-se",
    "dispõe", "dispoe", "disposições",
    "regulamenta", "regulamentado",
    "estabelece", "estabelecido",
    "institui", "instituído",
    "define", "definido",

    "art.", "artigo", "§", "parágrafo",
    "inciso", "alínea", "caput",

    "dá nova redação", "da nova redacao",
    "passa a ter a seguinte redação",
    "fica alterado", "ficam alterados",
    "fica incluído", "ficam incluídos",
    "fica excluído", "ficam excluídos",

    "nos termos da", "na forma da lei",
    "decreto", "portaria", "resolução",
    "lei nº", "lei no", "decreto nº", "portaria nº",

    "CONPORTOS", "conportos"
]

# =========================
# FUNÇÕES
# =========================

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

# =========================
# CORE
# =========================

def analisar_links(url_busca, palavras, status=None, progress=None):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    resumo = []

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

            # =========================
            # BLOQUEIO ABSOLUTO
            # =========================
            if any(p in texto for p in palavras_bloqueio):
                resumo.append({
                    "Documento": titulo,
                    "PDF": f"[PDF]({link})",
                    "Match": "0/0",
                    "Encontradas": "",
                    "Match Negativas": "0/0",
                    "Negativas encontradas": "BLOQUEADO",
                    "_score": -999
                })
                continue

            resultado_pos, resultado_neg = verificar_palavras(texto, palavras, palavras_negativas)

            encontradas = [p for p, v in resultado_pos.items() if v]
            encontradas_neg = [p for p, v in resultado_neg.items() if v]

            # =========================
            # SCORE INTELIGENTE
            # =========================

            score = 0

            # positivos
            for p in encontradas:
                score += pesos_positivos.get(p, 1)

            # padrão de representação
            padrao_representacao = (
                ("designa" in texto or "designados" in texto or "nomeia" in texto or "indica" in texto)
                and (
                    "para compor" in texto
                    or "compor" in texto
                    or "no âmbito do" in texto
                    or "integrantes" in texto
                    or "membros" in texto
                )
            )

            padrao_alteracao = (
            ("alterar" in texto or "altera" in texto)
            and (
                "designa" in texto
                or "designações" in texto
                or "designacoes" in texto
                or "representantes" in texto
                or "comitê" in texto
                or "conselho" in texto
            )
        )

            # ignora negativos estruturais se for representação
            if padrao_representacao:
                ignorar = ["art.", "artigo", "§", "inciso"]
                encontradas_neg = [p for p in encontradas_neg if p not in ignorar]

            # negativos
            for p in encontradas_neg:
                peso = pesos_negativos.get(p, 1)

                # se for representação, reduz impacto negativo
                if padrao_representacao:
                    peso *= 0.3

                score -= peso

            # boost forte
            if padrao_representacao:
                score += 20

            if padrao_alteracao:
                score += 20

            # detecção de nomes
            nomes = re.findall(r"[A-ZÁÉÍÓÚÂÊÔÃÕ][a-z]+ [A-ZÁÉÍÓÚÂÊÔÃÕ][a-z]+", texto)

            if len(nomes) >= 3:
                score += 10

            # =========================
            # MÉTRICAS ANTIGAS
            # =========================

            qtd = len(encontradas)
            total = len(palavras)

            qtd_neg = len(encontradas_neg)
            total_neg = len(palavras_negativas)

            resumo.append({
                "Documento": titulo,
                "PDF": f"[PDF]({link})",
                "Match": f"{qtd}/{total}",
                "Encontradas": ", ".join(encontradas),
                "Match Negativas": f"{qtd_neg}/{total_neg}",
                "Negativas encontradas": ", ".join(encontradas_neg),
                "_score": score
            })

        if progress: progress.progress(100)
        if status: status.markdown("✅ **Finalizado!**")

        return resumo

    finally:
        driver.quit()

# =========================
# TABELA
# =========================

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
            "Palavras negativas": r.get("Negativas encontradas", ""),
            "_score": r["_score"]
        })

    if not dados_tabela:
        df = pd.DataFrame(columns=["Documento", "Match", "PDF"])
        return df

    df = pd.DataFrame(dados_tabela)

    def destacar_linha(row):
        score = row["_score"]

        if score >= 15:
            return ["background-color: #c8e6c9"] * len(row)

        if score >= 8:
            return ["background-color: #e6f4ea"] * len(row)

        if score >= 3:
            return ["background-color: #fff9c4"] * len(row)

        return [""] * len(row)

    styled_df = df.style.apply(destacar_linha, axis=1)
    return styled_df