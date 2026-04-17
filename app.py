## app.py
from datetime import date
import streamlit as st
from linkbusca import obter_link_busca
from analise import analisar_links, gerar_tabela
from gerar_relatorio import gerar_csv_relatorio_downloud
from gerar_relatorio import gerar_csv_relatorio
from baixar_pdf import baixar_pdf
from baixar_pdf import criar_zip
import pathlib as path

st.title("Scanner Representações - MD")

# palavras_fixas = [
#     # estruturas colegiadas
#     "comitê", "comissao", "conselho", "grupo de trabalho",
#     "grupo de assessoramento", "grupo de assessoria",
#     "grupo de assessoria especial", "grupo conjunto",
#     "grupo especial", "grupo técnico", "grupo técnico de trabalho",
#     "grupo temporário", "subcomissao", "subcomite", "subgrupo",

#     # ação típica de representação
#     "designados", "designado", "designar",
#     "nomeados", "nomeado", "nomear",
#     "indicados", "indicado", "indicar",
#     "designa", "nomeia", "indica",

#     # composição de pessoas
#     "titular", "suplente", "membro", "membros",
#     "representante", "representantes",
#     "integrante", "integrantes",

#     # cargos dentro de comitês
#     "coordenador", "coordenadora",
#     "presidente", "vice-presidente",
#     "relator", "secretario", "secretária",

#     # padrões institucionais fortes
#     "ficam designados", "ficam nomeados", "ficam indicados",
#     "para compor", "compor o comite", "compor o conselho",
#     "no âmbito do", "no ambito do",

#     "ficam designados para compor",
#     "ficam designados os representantes",
#     "designados para compor",
#     "composição do comitê",
#     "titular e suplente",
#     "no âmbito do comitê"
# ]

entrada = st.text_input(
    "Digite palavras-chave adicionais (opcional)",
    ""
)

palavras_usuario = [p.strip() for p in entrada.split(",") if p.strip()]
# palavras = list(set(palavras_fixas + palavras_usuario))

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

    resumo = analisar_links(url_busca, palavras_usuario, status=status, progress=progress)

    # Gerar CSV
    gerar_csv_relatorio(resumo)
    csv = gerar_csv_relatorio_downloud(resumo)

    # baixar pdf
    baixar_pdf()

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
    
    

    col1, col2, col3 = st.columns()
    with col1:
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="relatorio.csv",
            mime="text/csv",
            on_click="ignore"
        )
    
    with col2:
        st.download_button(
            label="📥 Alta Chance",
            data=criar_zip("pdfs/alta_chance"),
            file_name="alta_chance.zip",
            mime="application/zip",
            on_click="ignore"
        )

    with col3:
        st.download_button(
            label="📥 Talvez",
            data=criar_zip("pdfs/talvez"),
            file_name="talvez.zip",
            mime="application/zip",
            on_click="ignore"
        )

    st.caption(f"Período consultado: {data_inicial_str} a {data_final_str}")