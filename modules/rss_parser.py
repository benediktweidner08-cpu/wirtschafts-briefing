"""
RSS Feed Parser für Wirtschaftsnachrichten
"""
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import yaml


class RSSParser:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.news_hours_filter = self.config.get('news_hours_filter', 24)
        self.cutoff_time = datetime.now() - timedelta(hours=self.news_hours_filter)
        
        # Hole RAW count (6 News statt 3)
        self.raw_count = self.config['news_count'].get('raw', 6)
    
    def parse_feed(self, url: str) -> List[Dict]:
        """Parse einzelnen RSS Feed"""
        try:
            feed = feedparser.parse(url)
            articles = []
            
            for entry in feed.entries:
                # Zeitstempel prüfen
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])
                
                # Nur News der letzten X Stunden
                if published and published < self.cutoff_time:
                    continue
                
                article = {
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', ''),
                    'published': published,
                    'source': feed.feed.get('title', 'Unbekannt')
                }
                articles.append(article)
            
            return articles
        
        except Exception as e:
            print(f"Fehler beim Parsen von {url}: {e}")
            return []
    
    def get_news_by_category(self, category: str) -> List[Dict]:
        """Hole News für eine bestimmte Kategorie"""
        feeds = self.config['rss_feeds'].get(category, [])
        all_articles = []
        
        for feed_url in feeds:
            articles = self.parse_feed(feed_url)
            all_articles.extend(articles)
        
        # Nach Datum sortieren (neueste zuerst)
        all_articles.sort(key=lambda x: x['published'] or datetime.min, reverse=True)
        
        # Duplikate entfernen (gleicher Titel)
        seen_titles = set()
        unique_articles = []
        for article in all_articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)
        
        # Limit auf RAW count (6 News)
        return unique_articles[:self.raw_count]
    
    def get_all_news(self) -> Dict[str, List[Dict]]:
        """Hole alle News für alle Kategorien (jeweils 6 Rohstoff-News)"""
        return {
            'allgemein': self.get_news_by_category('allgemein'),
            'finanzen': self.get_news_by_category('finanzen'),
            'krypto': self.get_news_by_category('krypto'),
            'forex': self.get_news_by_category('forex'),
            'tech': self.get_news_by_category('tech'),
            'rohstoffe': self.get_news_by_category('rohstoffe')
        }


if __name__ == "__main__":
    # Test
    parser = RSSParser("../config.yaml")
    news = parser.get_all_news()
    
    for category, articles in news.items():
        print(f"\n=== {category.upper()} ({len(articles)} News) ===")
        for article in articles[:3]:  # Erste 3 anzeigen
            print(f"- {article['title']}")
            print(f"  Quelle: {article['source']}")