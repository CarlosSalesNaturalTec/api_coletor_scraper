from fastapi import FastAPI, HTTPException
from scraper import scrape_and_save
from database import save_error_log

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Coletor Scraper no ar! Utilizando Newspaper3k."}

@app.post("/scrape-all")
def scrape_all_sites():
    """
    Aciona a raspagem de todas as URLs da coleção 'resultados_pesquisa'.
    """
    try:
        scrape_and_save()
        return {"status": "sucesso", "message": "Processo de raspagem concluido com sucesso."}
    except Exception as e:
        error_msg = f"Ocorreu um erro geral no endpoint /scrape-all: {e}"
        save_error_log(error_msg, context="scrape_all_sites_endpoint")
        raise HTTPException(status_code=500, detail=error_msg)