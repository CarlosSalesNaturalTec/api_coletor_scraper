import re
from datetime import datetime
from newspaper import Article
from database import get_db, save_error_log

def get_urls_from_firestore():
    """Busca URLs da coleção 'resultados_pesquisa' no Firestore."""
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
        error_msg = f"Erro ao buscar URLs do Firestore: {e}"
        print(error_msg)
        save_error_log(error_msg, context="get_urls_from_firestore")
    return urls

def save_failed_url(url, reason):
    """Salva uma URL que falhou ao ser raspada na coleção 'urls_com_falha'."""
    db = get_db()
    if not db:
        return

    try:
        db.collection('urls_com_falha').add({'url': url, 'reason': reason, 'timestamp': datetime.now()})
    except Exception as e:
        error_msg = f"Erro ao salvar URL com falha no Firestore: {e}"
        print(error_msg)
        save_error_log(error_msg, context="save_failed_url")

def scrape_and_save():
    """
    Busca URLs do Firestore, raspa-as usando newspaper3k,
    e salva os resultados ou registra as falhas.
    """
    urls = get_urls_from_firestore()
    db = get_db()

    if not db:
        print("Não foi possível conectar ao Firestore. Abortando.")
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
                print(f"A raspagem falhou para {url}, salvando em URLs com falha. Motivo: {reason}")
                save_failed_url(url, reason)
                continue

            data = extract_article_data(article, url)
            
            # Salva os dados raspados em uma nova coleção, por exemplo, 'scraped_articles'
            db.collection('scraped_articles').add(data)
            print(f"Raspado e salvo com sucesso: {url}")

        except Exception as e:
            reason = f"Exceção: {str(e)}"
            print(f"Ocorreu um erro ao raspar {url}: {e}")
            save_failed_url(url, reason)
            save_error_log(f"Erro ao raspar a URL: {url}. Exceção: {e}", context="scrape_and_save")

def has_significant_text(html):
    """
    Verifica se o HTML contém texto significativo dentro das tags <p> ou <article>.
    """
    from lxml import html as lxml_html
    
    if not html:
        return False
        
    tree = lxml_html.fromstring(html)
    
    # Verifica o texto nas tags <article>
    article_elements = tree.xpath('//article//text()')
    if any(text.strip() for text in article_elements):
        return True
        
    # Verifica o texto nas tags <p>
    p_elements = tree.xpath('//p//text()')
    if any(text.strip() for text in p_elements):
        return True
        
    return False

def extract_article_data(article, url):
    """Extrai e retorna dados estruturados do objeto do artigo."""
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