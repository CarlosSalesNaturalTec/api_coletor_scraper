Aplicação em Python+ FastAPI 
Nome da aplicação: api_coletor_scraper

Objetivo da aplicação: Fazer o scraping programático de páginas web para coletar o conteúdo textual bruto, metadados e dados estruturados de artigos/postagens.

Hospedagem da aplicação: Google Cloud Run

Ambiente de desenvolvimento: Windows

Instruções Detalhadas:

1 - Montar servidor em Python + FastAPI.
2 - Conectar-se com banco Firestore também hospedado na GCP. Utilize .ENV para credenciais. Faça esta conexão com o banco de maneira que possa ser reaproveitada pelo código em outras etapas.
3 - Obter no firestore a lista dos sites a serem pesquisados. 
4 - Fazer scraping destes sites utilizando bibliotecas: newspaper3k OU Playwright 
5 - Tentar fazer o scrapping inicialmente utilizando newspaper3k. usar o Playwright nas seguintes situações: newspaper3k falha ao baixar ; Conteúdo muito curto len(article.text) < 300 ; Título ausente ; Conteúdo HTML vazio Não há <article>, <p> com texto significativo
6 - Extrair conteúdo limpo: Título, corpo do texto, data (se disponível), domínio, etc
7 - Tentar detectar data de publicação utilizando metatags ou regex para inferir data 
8 - Retornar os dados extraídos em JSON 
9 - Armazenar resultado em Banco de Dados Firestore