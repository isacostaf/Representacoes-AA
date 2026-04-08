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
st.title("Scanner de resultados - DOU")

palavra = st.text_input("Digite a palavra-chave", "representantes")

if st.button("Verificar TODOS os resultados"):

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
        # 1. Pegar TODOS os resultados
        # -----------------------------
        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")

        st.write(f"🔎 Total de resultados encontrados: {len(resultados)}")

        links = []
        for r in resultados:
            titulo = r.text
            link = r.get_attribute("href")
            links.append((titulo, link))

        encontrados = []

        # -----------------------------
        # 2. Percorrer todos
        # -----------------------------
        for i, (titulo, link) in enumerate(links):

            st.write(f"➡️ Verificando {i+1}/{len(links)}")

            driver.get(link)
            driver.implicitly_wait(5)

            if pagina_tem_palavra(driver, palavra):
                encontrados.append((titulo, link))
                st.success(f"✅ Encontrado: {titulo}")

        # -----------------------------
        # 3. Resultado final
        # -----------------------------
        st.write("-----")
        st.write(f"🎯 Total com a palavra '{palavra}': {len(encontrados)}")

        for titulo, link in encontrados:
            st.markdown(f"[{titulo}]({link})")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()