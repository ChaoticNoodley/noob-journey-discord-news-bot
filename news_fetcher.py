import feedparser
import re
from typing import List, Dict
from datetime import datetime
from email.utils import parsedate_to_datetime

# Os link abaixo, podem ser alterados conforme o proposito
class NewsFetcher:
    def __init__(self):
        self.sources = {
            "windows": [
                "https://www.windowslatest.com/feed/"
            ],
            "linux": [
                "https://diolinux.com.br/feed",
                "https://9to5linux.com/feed/"
            ]
        }

    # UTIL
    def clean_html(self, text: str) -> str:
        clean = re.compile("<.*?>")
        return re.sub(clean, "", text).strip()

    def parse_date(self, entry) -> datetime:
        try:
            if hasattr(entry, "published"):
                return parsedate_to_datetime(entry.published)
        except Exception:
            pass
        return datetime.utcnow()

    # MAIN
    def fetch_latest_news(self, category: str, limit: int = 3) -> List[Dict]:
        if category not in self.sources:
            return []

        news_items = []
        seen_ids = set()

        for source in self.sources[category]:
            try:
                feed = feedparser.parse(source)

                if not feed.entries:
                    print(f"[WARN] Feed vazio ou inacessível: {source}")
                    continue

                for entry in feed.entries:
                    try:
                        title = entry.title
                        link = entry.link
                        news_id = entry.id if hasattr(entry, "id") else link

                        if news_id in seen_ids:
                            continue

                        seen_ids.add(news_id)

                        image_url = None

                        if "media_content" in entry:
                            image_url = entry.media_content[0]["url"]
                        elif "summary" in entry:
                            img_match = re.search(r'<img [^>]*src="([^"]+)"', entry.summary)
                            if img_match:
                                image_url = img_match.group(1)

                        if not image_url and "content" in entry:
                            img_match = re.search(
                                r'<img [^>]*src="([^"]+)"',
                                entry["content"][0].value
                            )
                            if img_match:
                                image_url = img_match.group(1)

                        summary = self.clean_html(entry.summary if "summary" in entry else "")
                        published_date = self.parse_date(entry)

                        news_items.append({
                            "id": news_id,
                            "title": title,
                            "link": link,
                            "summary": summary[:300] + "...",
                            "image_url": image_url,
                            "published": published_date.strftime("%d/%m/%Y %H:%M"),
                            "category": category,
                            "date_obj": published_date
                        })

                    except Exception as item_error:
                        print(f"[WARN] Erro ao processar notícia individual: {item_error}")
                        continue

            except Exception as feed_error:
                print(f"[ERROR] Erro ao acessar feed {source}: {feed_error}")
                continue

        news_items.sort(key=lambda x: x["date_obj"], reverse=True)
        return news_items[:limit]


# TEST LOCAL
if __name__ == "__main__":
    fetcher = NewsFetcher()
    print("Testando...\n")

    for cat in ["windows", "linux"]:
        news = fetcher.fetch_latest_news(cat, limit=3)
        if news:
            for n in news:
                print(f"[{cat.upper()}] {n['title']} ({n['published']})")
        else:
            print(f"[{cat.upper()}] Nenhuma notícia encontrada.")
