## app.py
from datetime import date
import streamlit as st
from linkbusca import obter_link_busca
from analise import analisar_links, gerar_tabela
from gerar_relatorio import gerar_csv_relatorio_downloud
from gerar_relatorio import gerar_csv_relatorio
from baixar_pdf import baixar_pdf
from baixar_pdf import criar_zip
from erro import csv_vazio
from env_email import enviar_email
import pathlib as path


def avancar_progresso(progress_bar, status_box, percentual, mensagem):
    valor = max(0, min(int(percentual), 100))
    progress_bar.progress(valor)
    status_box.markdown(mensagem)

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

# entrada = st.text_input(
#     "Digite palavras-chave adicionais (opcional)",
#     ""
# )

# palavras_usuario = [p.strip() for p in entrada.split(",") if p.strip()]
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

    avancar_progresso(progress, status, 15, "🌐 Preparando busca...")

    # Buscamos o link da pesquisa de hoje
    # Funcao do arquivo linkbusca.py
    url_busca = obter_link_busca(data_inicial_str, data_final_str)

    avancar_progresso(progress, status, 50, "🔎 Analisando documentos...")

    resumo = analisar_links(url_busca)

    avancar_progresso(progress, status, 70, "🧾 Gerando arquivo CSV...")

    # Gerar CSV
    gerar_csv_relatorio(resumo)

    avancar_progresso(progress, status, 80, "🧾 Preparando CSV para download...")
    csv = gerar_csv_relatorio_downloud(resumo)

    if csv_vazio("relatorio.csv"):
        avancar_progresso(progress, status, 100, "⚠️  Nenhum documento encontrado para o período informado.")
        st.warning(
            "Possivelmente não há arquivos disponíveis para essa data no sistema do DOU." 
            "Como o agente pode apresentar inconsistências, recomendamos a verificação manual diretamente no site do DOU."
        )
        st.caption(f"Periodo consultado: {data_inicial_str} a {data_final_str}")
        st.stop()

    avancar_progresso(progress, status, 90, "📥 Baixando PDFs...")

    # baixar pdf
    baixar_pdf()

    avancar_progresso(progress, status, 100, "✅ Processo completo!")

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
    
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name="relatorio.csv",
        mime="text/csv"
    )

    st.download_button(
        label="📥 Alta Chance",
        data=criar_zip("pdfs/alta_chance"),
        file_name="alta_chance.zip",
        mime="application/zip",
        on_click="ignore"
    )

    st.download_button(
        label="📥 Talvez",
        data=criar_zip("pdfs/talvez"),
        file_name="talvez.zip",
        mime="application/zip",
        on_click="ignore"
    )

    st.button(
        label="📧 Enviar email",
        on_click=enviar_email
    )

    st.caption(f"Período consultado: {data_inicial_str} a {data_final_str}")