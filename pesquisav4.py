import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# -----------------------------
# Verifica várias palavras no texto
# -----------------------------
def verificar_palavras(texto, palavras):
    texto = texto.lower()
    resultado = {}

    for palavra in palavras:
        resultado[palavra] = palavra.lower() in texto

    return resultado


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Busca no DOU por múltiplas palavras")

palavras_input = st.text_input(
    "Digite palavras-chave separadas por vírgula",
    "defesa, acordo, município"
)

if st.button("Buscar"):

    palavras = [p.strip() for p in palavras_input.split(",") if p.strip()]

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    resultados = []

    try:
        url_busca = "https://www.in.gov.br/consulta/-/buscar/dou?q=%22Minist%C3%A9rio+da+Defesa%22&s=todos&exactDate=personalizado&sortType=0&publishFrom=07-04-2026&publishTo=07-04-2026"
        driver.get(url_busca)

        time.sleep(2)

        elementos = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")

        st.write(f"🔎 {len(elementos)} resultados encontrados")

        # -----------------------------
        # Loop nos resultados
        # -----------------------------
        for el in elementos:
            titulo = el.text
            link = el.get_attribute("href")

            driver.get(link)
            time.sleep(1)

            paragrafos = driver.find_elements(By.CLASS_NAME, "dou-paragraph")
            texto_total = " ".join([p.text for p in paragrafos])

            verificacao = verificar_palavras(texto_total, palavras)

            resultados.append({
                "titulo": titulo,
                "link": link,
                "verificacao": verificacao
            })

            driver.back()
            time.sleep(1)

        # -----------------------------
        # 📊 RESUMO (PARTE IMPORTANTE)
        # -----------------------------
        st.markdown("## 📊 Resumo")

        for r in resultados:
            total = len(r["verificacao"])
            encontradas = sum(r["verificacao"].values())

            if encontradas > 0:
                st.markdown(f"### ✅ {r['titulo']}")
            else:
                st.markdown(f"### ❌ {r['titulo']}")

            st.markdown(f"**{encontradas}/{total} palavras encontradas**")

        # -----------------------------
        # 🔎 DETALHES
        # -----------------------------
        st.markdown("---")
        st.markdown("## 🔎 Detalhes")

        for r in resultados:
            st.markdown(f"### 📄 {r['titulo']}")

            encontradas = [p for p, v in r["verificacao"].items() if v]
            nao_encontradas = [p for p, v in r["verificacao"].items() if not v]

            st.write("✅ Encontradas:", encontradas if encontradas else "Nenhuma")
            st.write("❌ Não encontradas:", nao_encontradas if nao_encontradas else "Nenhuma")

            st.markdown(f"[🔗 Abrir documento]({r['link']})")

            st.markdown("---")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()