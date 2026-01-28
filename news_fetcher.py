import feedparser
import os
import re
from typing import List, Dict

class NewsFetcher:
    def __init__(self):
        self.sources = {
            "windows": "https://www.infomoney.com.br/tudo-sobre/windows/feed/",
            "linux": "https://diolinux.com.br/feed"
        }

    def clean_html(self, text: str ) -> str:
        """Remove tags HTML e limpa o texto."""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text).strip()

    def fetch_latest_news(self, category: str, limit: int = 3) -> List[Dict]:
        """Busca as notícias mais recentes das novas fontes em PT-BR."""
        if category not in self.sources:
            return []

        try:
            feed = feedparser.parse(self.sources[category])
            news_items = []

            for entry in feed.entries[:limit]:
                # Tenta pegar uma imagem do conteúdo ou do feed
                image_url = None
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                elif 'summary' in entry:
                    img_match = re.search(r'<img [^>]*src="([^"]+)"', entry.summary)
                    if img_match:
                        image_url = img_match.group(1)
                
                # Se ainda não achou imagem (comum no Diolinux), tenta no content
                if not image_url and 'content' in entry:
                    img_match = re.search(r'<img [^>]*src="([^"]+)"', entry[ 'content' ][0].value)
                    if img_match:
                        image_url = img_match.group(1)

                summary = self.clean_html(entry.summary if 'summary' in entry else "")
                
                news_items.append({
                    "id": entry.id if hasattr(entry, 'id') else entry.link,
                    "title": entry.title,
                    "link": entry.link,
                    "summary": summary[:300] + "...",
                    "image_url": image_url,
                    "published": entry.published if hasattr(entry, 'published') else "",
                    "category": category
                })
            return news_items
        except Exception as e:
            print(f"Erro ao buscar notícias de {category}: {e}")
            return []

if __name__ == "__main__":
    fetcher = NewsFetcher()
    print("Testando novas fontes em Português...")
    for cat in ["windows", "linux"]:
        news = fetcher.fetch_latest_news(cat, limit=1)
        if news:
            print(f"[{cat.upper()}] {news[0]['title']}")

