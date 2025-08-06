from fastapi import FastAPI, HTTPException
from database import get_db

app = FastAPI()

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
