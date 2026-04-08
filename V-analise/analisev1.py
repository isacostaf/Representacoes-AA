import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


# -----------------------------
# Função que verifica palavra no HTML
# -----------------------------
def pagina_tem_palavra(driver, palavra):
    paragrafos = driver.find_elements(By.CLASS_NAME, "dou-paragraph")

    texto_completo = " ".join([p.text for p in paragrafos])

    return palavra.lower() in texto_completo.lower()


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Teste - Primeiro resultado (HTML)")

palavra = st.text_input("Digite a palavra-chave", "representantes")

if st.button("Verificar primeiro resultado"):

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        url_busca = "https://www.in.gov.br/consulta/-/buscar/dou?q=%22Minist%C3%A9rio+da+Defesa%22&s=todos&exactDate=personalizado&sortType=0&publishFrom=07-04-2026&publishTo=07-04-2026"
        driver.get(url_busca)

        # -----------------------------
        # 1. Pegar o PRIMEIRO resultado
        # -----------------------------
        primeiro = driver.find_element(By.CSS_SELECTOR, "a[href*='/web/dou/']")

        titulo = primeiro.text
        link = primeiro.get_attribute("href")

        st.write("📄 Título:", titulo)

        # -----------------------------
        # 2. Abrir a página do resultado
        # -----------------------------
        driver.get(link)

        # (opcional) pequena espera pra garantir carregamento
        driver.implicitly_wait(5)

        # -----------------------------
        # 3. Verificar palavra no HTML
        # -----------------------------
        with st.spinner("Buscando no texto..."):
            tem = pagina_tem_palavra(driver, palavra)

        if tem:
            st.success(f"✅ Contém a palavra '{palavra}'")
        else:
            st.error(f"❌ NÃO contém a palavra '{palavra}'")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()