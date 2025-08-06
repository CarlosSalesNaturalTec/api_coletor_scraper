from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  
from database import get_db
from scraper import scrape_article

app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "API para coletar conteúdo de páginas web."}

@app.get("/sites")
def get_sites():
    """Fetches the list of sites to scrape from Firestore."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Could not connect to database.")

    sites_ref = db.collection('resultados_pesquisa')
    docs = sites_ref.stream()

    sites = [doc.to_dict().get('link') for doc in docs]
    return {"sites": sites}

@app.post("/scrape")
def scrape_and_save(request: ScrapeRequest):
    """Scrapes a single URL and saves the result to Firestore."""
    article_data = scrape_article(request.url)

    if not article_data:
        raise HTTPException(status_code=500, detail="Failed to scrape the article.")

    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Could not connect to database.")

    try:
        db.collection('scraped_articles').add(article_data)
        return {"status": "success", "data": article_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to Firestore: {e}")
