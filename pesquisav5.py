import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd


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

# 🔒 palavras fixas
palavras_fixas = [
    "instituir", "institui", "representantes",
    "indicacao", "indicações", "indicacoes",
    "ficam designados", "fica designado",
    "ficam designadas", "fica designada",
    "grupo de trabalho", "grupo de trabalhos",
    "grupo de trabalaho", "grupo trabalho",
    "comite", "comitê", "comites", "comitês",
    "comissao", "comissão", "comissoes", "comissões"
]

entrada = st.text_input(
    "Digite palavras-chave adicionais (opcional)",
    ""
)

palavras_usuario = [p.strip() for p in entrada.split(",") if p.strip()]

# junta tudo
palavras = list(set(palavras_fixas + palavras_usuario))

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

        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")
        links = [(r.text, r.get_attribute("href")) for r in resultados]

        st.write(f"🔎 Total: {len(links)} resultados")

        resumo = []
        detalhes = []

        # -----------------------------
        # percorre documentos
        # -----------------------------
        for titulo, link in links:

            driver.get(link)
            driver.implicitly_wait(5)

            texto = pegar_texto(driver)
            resultado = verificar_palavras(texto, palavras)

            encontradas = [p for p, v in resultado.items() if v]
            qtd = len(encontradas)
            total = len(palavras)

            resumo.append({
                "Documento": titulo,
                "Match": f"{qtd}/{total}",
                "PDF": f"[Ver PDF]({link})",
                "Encontradas": ", ".join(encontradas)
            })

            detalhes.append((titulo, link, resultado))

        # -----------------------------
        # 📊 TABELA RESUMO (CORRETA)
        # -----------------------------
        st.subheader("📊 Resumo")

        dados_tabela = []

        for r in resumo:
            link_pdf = r["PDF"].split("(")[1].replace(")", "")

            dados_tabela.append({
                "Documento": r["Documento"],
                "Match": r["Match"],
                "Ver PDF": link_pdf,
                "Palavras encontradas": r["Encontradas"]
            })

        df = pd.DataFrame(dados_tabela)

        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Ver PDF": st.column_config.LinkColumn(
                    "Ver PDF",
                    display_text="ver pdf"
                )
            }
        )

        # -----------------------------
        # 🧾 RODAPÉ
        # -----------------------------
        st.markdown(
            f"<p style='color:gray; font-size:12px;'>Palavras pesquisadas: {', '.join(palavras)}</p>",
            unsafe_allow_html=True
        )

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()