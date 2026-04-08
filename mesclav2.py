from linkbusca import obter_link_busca
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

    # UI de carregamento
    status = st.empty()
    progress = st.progress(0)

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # -----------------------------
        # 🔍 ETAPA 1: BUSCA
        # -----------------------------
        status.markdown("🔎 **Filtrando buscas...**")
        progress.progress(10)

        url_busca = obter_link_busca()

        status.markdown("🌐 **Abrindo resultados...**")
        progress.progress(20)

        driver.get(url_busca)
        driver.implicitly_wait(5)

        resultados = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")
        links = [(r.text, r.get_attribute("href")) for r in resultados]

        total_links = len(links)

        status.markdown(f"📄 **{total_links} documentos encontrados**")
        progress.progress(30)

        st.write(f"🔎 Total: {total_links} resultados")

        resumo = []
        detalhes = []

        # -----------------------------
        # 🔁 ETAPA 2: ANÁLISE
        # -----------------------------
        for i, (titulo, link) in enumerate(links):

            # progresso dinâmico (30% → 90%)
            progresso = 30 + int((i / total_links) * 60)
            progress.progress(progresso)

            status.markdown(
                f"📊 **Analisando documentos {i+1}/{total_links}**<br>"
                f"<small>{titulo}</small>",
                unsafe_allow_html=True
            )

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
                "PDF": f"[PDF]({link})",
                "Encontradas": ", ".join(encontradas)
            })

            detalhes.append((titulo, link, resultado))

        # -----------------------------
        # ✅ FINALIZAÇÃO
        # -----------------------------
        progress.progress(100)
        status.markdown("✅ **Finalizado! Gerando tabela...**")

        # -----------------------------
        # 📊 TABELA
        # -----------------------------
        st.subheader("📊 Resumo")

        dados_tabela = []

        for r in resumo:
            link_pdf = r["PDF"].split("(")[1].replace(")", "")

            dados_tabela.append({
                "Documento": r["Documento"],
                "Match": r["Match"],
                "PDF": f'<a href="{link_pdf}" target="_blank">ver pdf</a>',
                "Palavras encontradas": r["Encontradas"]
            })

        df = pd.DataFrame(dados_tabela)

        # cor
        df["_qtd"] = df["Match"].apply(lambda x: int(x.split("/")[0]))

        def destacar_linha(row):
            if row["_qtd"] > 0:
                return ["background-color: #e6f4ea"] * len(row)
            return [""] * len(row)

        styled_df = df.style.apply(destacar_linha, axis=1)
        styled_df = styled_df.hide(axis="columns", subset=["_qtd"])

        st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

        # rodapé
        st.markdown(
            f"<p style='color:gray; font-size:12px;'>Palavras pesquisadas: {', '.join(palavras)}</p>",
            unsafe_allow_html=True
        )

        # limpa loading no final (opcional)
        status.markdown("🎉 **Concluído!**")

    except Exception as e:
        st.error(f"Erro: {e}")

    finally:
        driver.quit()