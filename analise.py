from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# =========================
# 🎯 PESOS POSITIVOS
# =========================
PESOS_POSITIVOS = {
    "fica instituído": 7,
    "será composto": 7,
    "fica instituído": 7,
    "designar os seguintes membros": 7,
    "alterar designações": 7,
    "para compor": 2,

    "comitê": 1,
    "comissao": 1,
    "conselho": 1,

    "grupo de trabalho": 1,
    "grupo de assessoramento": 1,
    "grupo de assessoria": 1,
    "grupo conjunto": 1,
    "grupo especial": 1,
    "grupo técnico": 1,
    "subcomissao": 1,
    "subcomite": 1,
    "subgrupo": 1,

    "designados": 1,
    "designado": 1,
    "nomeados": 1,
    "nomeado": 1,
    "indicados": 1,
    "indicado": 1,
    "membro": 1,
    "representante": 1,
}

# =========================
# 🚫 PESOS NEGATIVOS
# =========================
PESOS_NEGATIVOS = {
    "incluir": 1,
    "incluído": 1,
    "incluída": 1,

    "substitui": 1,
    "substituído": 1,
    "substituída": 1,

    "excluir": 1,
    "excluído": 1,
    "excluída": 1,
    "regulamenta": 1,
    "institui": 1,
    "estabelece": 1,
    "disposições": 1,
    "resolução": 1,
    "licitação": 1,
}

# =========================
# 📄 TEXTO DO DOCUMENTO
# =========================
def pegar_texto(driver):
    paragrafos = driver.find_elements(By.CLASS_NAME, "dou-paragraph")
    return " ".join([p.text for p in paragrafos]).lower()

# =========================
# 🧠 SCORE
# =========================
def calcular_score(texto):
    score_pos = sum(
        peso for palavra, peso in PESOS_POSITIVOS.items()
        if palavra in texto
    )

    score_neg = sum(
        peso for palavra, peso in PESOS_NEGATIVOS.items()
        if palavra in texto
    )

    return score_pos - score_neg

# =========================
# 🔎 BOTÃO PRÓXIMA PÁGINA
# =========================
def _encontrar_botao_proxima(driver):
    try:
        botao = driver.find_element(By.ID, "rightArrow")
    except Exception:
        return None

    if not botao.is_displayed():
        return None

    classes = (botao.get_attribute("class") or "").lower()
    aria_disabled = (botao.get_attribute("aria-disabled") or "").lower()
    disabled_attr = botao.get_attribute("disabled")

    if "disabled" in classes or aria_disabled == "true" or disabled_attr is not None:
        return None

    return botao

# =========================
# 📄 PAGINAÇÃO
# =========================
def _coletar_links_paginados(driver, status=None, max_paginas=200):
    wait = WebDriverWait(driver, 12)
    links_unicos = []
    vistos = set()
    pagina = 1

    while pagina <= max_paginas:
        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")

        for r in resultados:
            href = r.get_attribute("href")
            if not href or href in vistos:
                continue

            titulo = (r.text or "").strip()
            vistos.add(href)
            links_unicos.append((titulo if titulo else "Sem titulo", href))

        # if status:
        #     status.markdown(f"🔎 **Coletando resultados... página {pagina} ({len(links_unicos)} links únicos)**")

        botao_proxima = _encontrar_botao_proxima(driver)
        if not botao_proxima:
            break

        url_antes = driver.current_url
        marcador = resultados[0] if resultados else None

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            botao_proxima
        )

        try:
            botao_proxima.click()
        except Exception:
            driver.execute_script("arguments[0].click();", botao_proxima)

        try:
            if marcador:
                wait.until(EC.staleness_of(marcador))
            else:
                wait.until(lambda d: d.current_url != url_antes)
        except TimeoutException:
            break

        pagina += 1

    return links_unicos

# =========================
# 🚀 ANÁLISE PRINCIPAL
# =========================
def analisar_links(url_busca, palavras_usuario, status=None, progress=None):
    palavras = list(set(list(PESOS_POSITIVOS.keys()) + palavras_usuario))

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    resumo = []

    try:
        driver.get(url_busca)
        driver.implicitly_wait(5)

        links = _coletar_links_paginados(driver, status=status)
        total = len(links)

        if status: status.markdown(f"🌐 **Abrindo resultados... {total} encontrados**")
        if progress: progress.progress(20)

        for i, (titulo, link) in enumerate(links):
            if progress:
                progress.progress(int((i / max(total, 1)) * 100))

            if status:
                status.markdown(
                    f"📊 **Analisando documentos {i+1}/{total}**<br><small>{titulo}</small>",
                    unsafe_allow_html=True
                )

            driver.get(link)
            driver.implicitly_wait(5)

            texto = pegar_texto(driver)
            score = calcular_score(texto)

            positivas = [p for p in PESOS_POSITIVOS if p in texto]
            negativas = [p for p in PESOS_NEGATIVOS if p in texto]

            resumo.append({
                "Documento": titulo,
                "PDF": f"[PDF]({link})",
                "Score": score,
                "Palavras positivas": ", ".join(positivas),
                "Palavras negativas": ", ".join(negativas),
            })

        if status:
            status.markdown("✅ Finalizado!")

        return resumo

    finally:
        driver.quit()

# =========================
# 📊 TABELA FINAL (STREAMLIT)
# =========================
def gerar_tabela(resumo):
    df = pd.DataFrame(resumo)

    # evita crash se vazio
    if df.empty:
        return df

    def destacar_linha(row):
        score = row["Score"]

        if score >= 5:
            return ["background-color: #e6f4ea"] * len(row)

        if score > 0:
            return ["background-color: #fff9c4"] * len(row)

        return [""] * len(row)

    styled_df = df.style.apply(destacar_linha, axis=1)

    # mantém HTML do link PDF funcionando
    return styled_df