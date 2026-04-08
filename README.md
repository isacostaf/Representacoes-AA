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

**App principal:** *app.py*
**Função Link:** *linkbusca.py*
**Função Análise e Gráficos:** *analise.py*

**Pastas:** 
*V-arquivo: versões do arquivo arquivo.py e evolução*

### App Princial:
🔗 app.py
*Esse é o app principal e único do projeto*
*Depende de arquivos: linkbusca.py e analise.py*

### Link Busca:
🔗 linkbusca.py
*Função que aplica os filtros necessários e realiza a busca filtrada do dia de hoje com as preferências necessárias*
*Retorna o link com o resultado de busca exato*

### Analise:
🔗 analise.py
*Função que aplica analisa e gera grafico dos documentos encontrados no link*
*Procura pelas palavras chaves*

### Analise VERSÕES:
🔗 analiseV.py
*Versões e evoluções do algoritmo de pesquisa e análise dos arquivos encontrados*

### Mescla:
🔗 mescla.py
*Mesclagem do algoritmo de retorno de link com o algoritmo de pesquisa e análise dos arquivos*
*analise.py + linkbusca.py*
*Com alterações necessárias*
*Para testar necessita estar na mesma pasta que o analise e o link busca usados*

### Versões:
🔗 VESOES.md
*documento de rastreamento de versões e evoluções de arquivos*

# To-do
- [ ] concertar link correto
- [ ] deixar mais rápido
- [ ] apenas chamar a função pesquisa em app.py