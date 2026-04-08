# Como rodar:
``pip install streamlit pandas requests``
``pip install streamlit selenium webdriver-manager``
``pip install pdfplumber``

### Rodar app:
``streamlit run app.py``

### Como rodar qualquer streamlit:
``streamlit run arquivo.py``

# Arquivos:
Manual de arquivos

### App Princial:
🔗 app.py
*Esse é o app principal e único do projeto*
*Depende de arquivos: linkbusca.py*

### Link Busca:
🔗 linkbusca.py
*Função que aplica os filtros necessários e realiza a busca filtrada do dia de hoje com as preferências necessárias*
*Retorna o link com o resultado de busca exato*

### Pesquisa:
🔗 pesquisa.py
*Versões e evoluções do algoritmo de pesquisa e análise dos arquivos encontrados*

### Mescla:
🔗 mescla.py
*Mesclagem do algoritmo de retorno de link com o algoritmo de pesquisa e análise dos arquivos*
*Pesquisa.py + linkbusca.py*
*Com alterações necessárias*

### Versões:
🔗 VESOES.md
*documento de rastreamento de versões e evoluções de arquivos*

# To-do
- [ ] concertar link correto
- [ ] deixar mais rápido
- [ ] apenas chamar a função pesquisa em app.py