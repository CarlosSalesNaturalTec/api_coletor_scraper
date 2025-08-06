
import re
from datetime import datetime
from newspaper import Article
from playwright.sync_api import sync_playwright

def scrape_article(url):
    """
    Scrapes an article using newspaper3k first, with a fallback to Playwright
    if initial scraping fails or the content is insufficient.
    """
    try:
        # Attempt 1: Scrape with newspaper3k
        article = Article(url)
        article.download()
        article.parse()

        # Check for conditions to use Playwright
        if not article.title or len(article.text) < 300:
            raise ValueError("Initial scrape insufficient, trying Playwright.")

        return extract_article_data(article, url, "newspaper")

    except Exception as e:
        print(f"Newspaper3k failed: {e}. Falling back to Playwright.")
        # Attempt 2: Scrape with Playwright
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url)
                html_content = page.content()
                browser.close()

                # Use newspaper3k to parse the HTML from Playwright
                article = Article(url)
                article.set_html(html_content)
                article.parse()

                if not article.title and not article.text:
                     raise ValueError("Playwright also failed to extract content.")

                return extract_article_data(article, url, "playwright")
        except Exception as playwright_error:
            print(f"Playwright scraping also failed: {playwright_error}")
            return None


def extract_article_data(article, url, source_library):
    """Extracts and returns structured data from the article object, including the source library."""
    publish_date = article.publish_date

    # Attempt to find date with regex if not found by newspaper
    if not publish_date:
        # Regex for various date formats
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # DD/MM/YYYY
            r'(\w+\s\d{1,2},\s\d{4})' # Month D, YYYY
        ]
        for pattern in date_patterns:
            match = re.search(pattern, article.html)
            if match:
                try:
                    publish_date = datetime.strptime(match.group(1), '%Y-%m-%d') # Adjust format as needed
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
        "source_library": source_library
    }
