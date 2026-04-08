import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# -----------------------------
# Função que pega texto da página
# -----------------------------
def pegar_texto(driver):
    paragrafos = driver.find_elements(By.CLASS_NAME, "dou-paragraph")
    return " ".join([p.text for p in paragrafos]).lower()


# -----------------------------
# Função que verifica múltiplas palavras
# -----------------------------
def verificar_palavras(texto, palavras):
    resultado = {}
    for p in palavras:
        resultado[p] = p.lower() in texto
    return resultado


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Scanner DOU - Multi Palavras")

# 🔒 palavras fixas (ocultas do usuário)
palavras_fixas = [
    # originais
    "instituir", "institui", "representantes",

    # indicação
    "indicacao", "indicações", "indicacao", "indicacoes",

    # designados
    "ficam designados",
    "fica designado",
    "ficam designadas",
    "fica designada",

    # grupo de trabalho (com erros comuns)
    "grupo de trabalho",
    "grupo de trabalhos",
    "grupo de trabalaho",   # erro comum
    "grupo trabalho",

    # comitê
    "comite", "comitê", "comites", "comitês",

    # comissão
    "comissao", "comissão", "comissoes", "comissões"
]

entrada = st.text_input(
    "Digite palavras-chave adicionais (opcional)",
    ""
)

# palavras do usuário
palavras_usuario = [p.strip() for p in entrada.split(",") if p.strip()]

# 🔗 junta tudo (sem duplicar)
palavras = list(set(palavras_fixas + palavras_usuario))

# (opcional) mostrar de forma discreta
st.caption("Inclui automaticamente: instituir, institui, representantes, indicação, ficam designados, grupo de trabalho, comitê, comissão (e todas suas variações)")
if st.button("Verificar TODOS os resultados"):

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        url_busca = "https://www.in.gov.br/consulta/-/buscar/dou?q=%22+Minist%C3%A9rio+da+Defesa%22&s=todos&exactDate=personalizado&sortType=0&publishFrom=08-04-2026&publishTo=08-04-2026"
        driver.get(url_busca)

        driver.implicitly_wait(5)

        # -----------------------------
        # pegar todos resultados
        # -----------------------------
        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")

        links = [(r.text, r.get_attribute("href")) for r in resultados]

        st.write(f"🔎 Total: {len(links)} resultados")

        # -----------------------------
        # percorrer documentos
        # -----------------------------
        for i, (titulo, link) in enumerate(links):

            st.write(f"---")
            st.write(f"📄 {i+1}. {titulo}")

            driver.get(link)
            driver.implicitly_wait(5)

            texto = pegar_texto(driver)
            resultado = verificar_palavras(texto, palavras)

            # -----------------------------
            # mostrar resultado por palavra
            # -----------------------------
            for palavra, tem in resultado.items():
                if tem:
                    st.write(f"✅ {palavra}")
                else:
                    st.write(f"❌ {palavra}")

            # link do documento
            st.markdown(f"[Abrir documento]({link})")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()