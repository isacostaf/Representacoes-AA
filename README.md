# Representacoes-AA (Node.js + EJS)

Aplicacao para buscar e analisar publicacoes do DOU com classificacao de chance de representacao.

## Stack
- Front-end: EJS
- Back-end: Node.js + Express
- Automacao de busca e geracao de PDF: Puppeteer (compativel com Vercel)

## Rodando localmente
1. Instale as dependencias:
	npm install
2. Configure variaveis de ambiente:
	copie modelo.env para .env e preencha os valores
3. Inicie em modo desenvolvimento:
	npm run dev
4. Acesse:
	http://localhost:3000

## Deploy na Vercel
- Entrada serverless: api/index.js
- Rotas: vercel.json
- Em ambiente Vercel, os arquivos temporarios sao gerados em /tmp

## Variaveis de ambiente
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- EMAIL_FROM
- EMAIL_TO
