## atualmente utiliza:
## mesclav3.py

from datetime import date

import streamlit as st
from linkbusca import obter_link_busca
from analise import analisar_links, gerar_tabela

st.title("Scanner Representações - MD")

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
palavras = list(set(palavras_fixas + palavras_usuario))

st.caption("Inclui automaticamente: instituir, institui, representantes, indicação, ficam designados, grupo de trabalho, comitê, comissão (e todas suas variações)")

col_data_inicial, col_data_final = st.columns(2)
with col_data_inicial:
    data_inicial = st.date_input("Data inicial", value=date.today(), format="DD/MM/YYYY")
with col_data_final:
    data_final = st.date_input("Data final", value=date.today(), format="DD/MM/YYYY")

if st.button("Verificar TODOS os resultados"):
    if data_inicial > data_final:
        st.error("A data inicial não pode ser maior que a data final.")
        st.stop()

    status = st.empty()
    progress = st.progress(0)

    data_inicial_str = data_inicial.strftime("%d/%m/%Y")
    data_final_str = data_final.strftime("%d/%m/%Y")

    # Buscamos o link da pesquisa de hoje
    # Funcao do arquivo linkbusca.py
    url_busca = obter_link_busca(data_inicial_str, data_final_str)

    # Analisamos os arquivos
    # Funcao do arquivo analise.py
    resumo = analisar_links(url_busca, palavras, status=status, progress=progress)

    # Geramos tabela
    # Funcao do arquivo analise.py
    styled_df = gerar_tabela(resumo)

    st.subheader("📊 Resultado")
    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

    st.markdown(
        f"<p style='color:gray; font-size:12px;'>Palavras pesquisadas: {', '.join(palavras)}</p>",
        unsafe_allow_html=True
    )
    st.caption(f"Período consultado: {data_inicial_str} a {data_final_str}")   