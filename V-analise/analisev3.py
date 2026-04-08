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

entrada = st.text_input(
    "Digite palavras-chave separadas por vírgula",
    "representantes, defesa"
)

if st.button("Verificar TODOS os resultados"):

    palavras = [p.strip() for p in entrada.split(",") if p.strip()]

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        url_busca = "https://www.in.gov.br/consulta/-/buscar/dou?q=%22Minist%C3%A9rio+da+Defesa%22&s=todos&exactDate=personalizado&sortType=0&publishFrom=07-04-2026&publishTo=07-04-2026"
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