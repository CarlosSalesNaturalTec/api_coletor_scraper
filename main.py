from fastapi import FastAPI, HTTPException
from scraper import scrape_and_save

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "api_coletor_scraper no ar! Utilizando Newspaper3k."}

@app.post("/scrape-all")
def scrape_all_sites():
    """
    Triggers the scraping of all URLs from the 'resultados_pesquisa' collection.
    """
    try:
        scrape_and_save()
        return {"status": "success", "message": "Scraping process initiated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")