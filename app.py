from datetime import date

import streamlit as st
from linkbusca import obter_link_busca
from analise import analisar_links, gerar_tabela
from gerar_relatorio import gerar_csv_relatorio

st.title("Scanner Representações - MD")

palavras_fixas = [
    # estruturas colegiadas
    "comitê", "comissao", "conselho", "grupo de trabalho",
    "grupo de assessoramento", "grupo de assessoria",
    "grupo de assessoria especial", "grupo conjunto",
    "grupo especial", "grupo técnico", "grupo técnico de trabalho",
    "grupo temporário", "subcomissao", "subcomite", "subgrupo",
]

entrada = st.text_input(
    "Digite palavras-chave adicionais (opcional)",
    ""
)

palavras_usuario = [p.strip() for p in entrada.split(",") if p.strip()]

# Junta palavras fixas + usuário
palavras = list(set(palavras_fixas + palavras_usuario))

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

    url_busca = obter_link_busca(data_inicial_str, data_final_str)

    resumo = analisar_links(url_busca, palavras, status=status, progress=progress)

    styled_df = gerar_tabela(resumo)

    st.subheader("📊 Resultado")

    # Legenda
    st.markdown("""
    <div style="font-size:14px; margin-bottom:10px;">
    🟢 <b>Verde:</b> cerca de 90% de chance de ser uma representação correta.<br>
    🟡 <b>Amarelo:</b> provavelmente <b>não</b> é uma representação, mas vale a pena conferir manualmente.
    </div>
    """, unsafe_allow_html=True)

    # Aviso importante
    st.markdown("""
    <div style="font-size:13px; color:#b00020; margin-bottom:15px;">
    ⚠️ <b>Atenção:</b> Esta análise é feita por IA e pode conter erros. 
    A verificação humana continua sendo essencial e não deve ser dispensada.
    </div>
    """, unsafe_allow_html=True)

    # Tabela
    st.markdown(styled_df.to_html(escape=False), unsafe_allow_html=True)

    # Gerar CSV
    gerar_csv_relatorio(resumo)

    # Palavras usadas
    st.markdown(
        f"<p style='color:gray; font-size:12px;'>Palavras pesquisadas: {', '.join(palavras)}</p>",
        unsafe_allow_html=True
    )

    st.caption(f"Período consultado: {data_inicial_str} a {data_final_str}")