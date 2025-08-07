import re
from datetime import datetime
from newspaper import Article
from database import get_db

def get_urls_from_firestore():
    """Fetches URLs from the 'resultados_pesquisa' collection in Firestore."""
    db = get_db()
    if not db:
        return []
    
    urls = []
    try:
        collection_ref = db.collection('resultados_pesquisa')
        for doc in collection_ref.stream():
            data = doc.to_dict()
            if 'link' in data:
                urls.append(data['link'])
    except Exception as e:
        print(f"Error fetching URLs from Firestore: {e}")
    return urls

def save_failed_url(url, reason):
    """Saves a URL that failed to be scraped to the 'urls_com_falha' collection."""
    db = get_db()
    if not db:
        return

    try:
        db.collection('urls_com_falha').add({'url': url, 'reason': reason, 'timestamp': datetime.now()})
    except Exception as e:
        print(f"Error saving failed URL to Firestore: {e}")

def scrape_and_save():
    """
    Fetches URLs from Firestore, scrapes them using newspaper3k,
    and saves the results or logs failures.
    """
    urls = get_urls_from_firestore()
    db = get_db()

    if not db:
        print("Could not connect to Firestore. Aborting.")
        return

    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()

            failure_reasons = []
            if not article.title:
                failure_reasons.append("Título ausente")
            if len(article.text) < 300:
                failure_reasons.append(f"Conteúdo muito curto (len: {len(article.text)})")
            if not article.html:
                failure_reasons.append("Conteúdo HTML vazio")
            if not has_significant_text(article.html):
                failure_reasons.append("Não há <article> ou <p> com texto significativo")

            if failure_reasons:
                reason = ", ".join(failure_reasons)
                print(f"Scraping failed for {url}, saving to failed URLs. Reason: {reason}")
                save_failed_url(url, reason)
                continue

            data = extract_article_data(article, url)
            
            # Save the scraped data to a new collection, e.g., 'scraped_articles'
            db.collection('scraped_articles').add(data)
            print(f"Successfully scraped and saved: {url}")

        except Exception as e:
            reason = f"Exception: {str(e)}"
            print(f"An error occurred while scraping {url}: {e}")
            save_failed_url(url, reason)

def has_significant_text(html):
    """
    Checks if the HTML contains significant text within <p> or <article> tags.
    """
    from lxml import html as lxml_html
    
    if not html:
        return False
        
    tree = lxml_html.fromstring(html)
    
    # Check for text in <article> tags
    article_elements = tree.xpath('//article//text()')
    if any(text.strip() for text in article_elements):
        return True
        
    # Check for text in <p> tags
    p_elements = tree.xpath('//p//text()')
    if any(text.strip() for text in p_elements):
        return True
        
    return False

def extract_article_data(article, url):
    """Extracts and returns structured data from the article object."""
    publish_date = article.publish_date

    if not publish_date:
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{2}/\d{2}/\d{4})',
            r'(\w+\s\d{1,2},\s\d{4})'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, article.html)
            if match:
                try:
                    publish_date = datetime.strptime(match.group(1), '%Y-%m-%d')
                    break
                except ValueError:
                    continue

    return {
        "title": article.title,
        "text": article.text,
        "authors": article.authors,
        "publish_date": publish_date.isoformat() if publish_date else None,
        "top_image": article.top_image,
        "url": url,
        "domain": url.split('/')[2],
        "scraped_by": "newspaper3k",
        "scraped_at": datetime.now().isoformat()
    }