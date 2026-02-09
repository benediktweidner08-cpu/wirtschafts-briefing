#!/usr/bin/env python3
"""
Wirtschafts-Briefing Generator
Tägliches Email-Briefing mit Wirtschaftsnews und Marktdaten
"""

from modules.rss_parser import RSSParser
from modules.market_data import MarketData
from modules.relevance_filter import RelevanceFilter
from modules.summarizer import NewsSummarizer
from modules.email_sender import EmailSender
from modules.pdf_generator import PDFGenerator
from datetime import datetime
import sys
import yaml


def main():
    print("=" * 60)
    print("WIRTSCHAFTS-BRIEFING GENERATOR")
    print(f"Gestartet: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Config laden
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    try:
        # 1. RSS-Feeds parsen (6 News pro Kategorie)
        print("\n[1/7] 📰 Parse RSS-Feeds (je 6 News)...")
        parser = RSSParser()
        raw_news = parser.get_all_news()
        
        total_raw = sum(len(articles) for articles in raw_news.values())
        print(f"✅ {total_raw} Roh-News gefunden")
        for category, articles in raw_news.items():
            print(f"   - {category}: {len(articles)} News")
        
        # 2. Relevanz-Filter (auf Top 3 reduzieren)
        print("\n[2/7] 🎯 Filtere auf relevanteste News...")
        relevance_filter = RelevanceFilter()
        filtered_news = relevance_filter.filter_all_categories(raw_news)
        
        total_filtered = sum(len(articles) for articles in filtered_news.values())
        print(f"✅ {total_filtered} relevante News nach Filter")
        
        # 3. Marktdaten abrufen
        print("\n[3/7] 📈 Hole Marktdaten...")
        market = MarketData()
        market_data = market.get_all_markets()
        
        total_quotes = sum(len(quotes) for quotes in market_data.values())
        print(f"✅ {total_quotes} Kurse abgerufen")
        
        # 4. News mit Claude zusammenfassen
        print("\n[4/7] 🤖 Fasse gefilterte News zusammen...")
        summarizer = NewsSummarizer()
        summarized_news = summarizer.summarize_all(filtered_news)
        print("✅ Zusammenfassungen erstellt")
        
        # 5. PDF erstellen (falls aktiviert)
        pdf_path = None
        if config['output'].get('generate_pdf', True):
            print("\n[5/7] 📄 Erstelle PDF...")
            pdf_gen = PDFGenerator()
            pdf_path = pdf_gen.generate_pdf(market_data, summarized_news)
        else:
            print("\n[5/7] ⏭️  PDF-Erstellung übersprungen")
        
        # 6. Email erstellen (falls aktiviert)
        if config['output'].get('send_email', True):
            print("\n[6/7] 📧 Erstelle Email...")
            sender = EmailSender()
            
            print("\n[7/7] 📤 Sende Briefing...")
            sender.send_briefing(market_data, summarized_news)
        else:
            print("\n[6/7] ⏭️  Email-Versand übersprungen")
            print("\n[7/7] ⏭️  Kein Email-Versand")
        
        print("\n" + "=" * 60)
        print("✅ BRIEFING ERFOLGREICH ERSTELLT")
        if pdf_path:
            print(f"📄 PDF: {pdf_path}")
        print("=" * 60)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

