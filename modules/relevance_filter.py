"""
Relevanz-Filter mit Claude API
Bewertet Wirtschaftsnachrichten nach ihrer Relevanz
"""
from anthropic import Anthropic
from typing import List, Dict
import os
from dotenv import load_dotenv


class RelevanceFilter:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY nicht in .env gefunden")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"
    
    def evaluate_relevance(self, articles: List[Dict], category: str) -> List[Dict]:
        """
        Bewertet eine Liste von Artikeln nach Wirtschaftsrelevanz
        Gibt die Top 3 zurück
        """
        if len(articles) == 0:
            return []
        
        # Wenn nur 3 oder weniger, direkt zurückgeben
        if len(articles) <= 3:
            return articles
        
        # Erstelle Prompt mit allen Headlines
        headlines = "\n".join([
            f"{i+1}. {article['title']}" 
            for i, article in enumerate(articles)
        ])
        
        category_context = self._get_category_context(category)
        
        prompt = f"""Du bist ein Finanz-Analyst. Bewerte diese {len(articles)} Nachrichten aus der Kategorie "{category}" nach ihrer Wirtschaftsrelevanz für Investoren und Trader.

{category_context}

HEADLINES:
{headlines}

BEWERTUNGSKRITERIEN:
- Markteinfluss (Börsen, Kurse, Indizes)
- Investor-Relevanz (Investment-Entscheidungen)
- Wirtschaftliche Bedeutung (nicht nur Politik/Lokales)
- Aktualität und Dringlichkeit

AUSGABE:
Gib NUR die Nummern der TOP 3 relevantesten Headlines zurück, getrennt durch Komma.
Format: 1,4,2

Antwort (nur Nummern):"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Parse Antwort (z.B. "1,4,2")
            result = response.content[0].text.strip()
            indices = [int(x.strip()) - 1 for x in result.split(',')]  # -1 weil 0-indexiert
            
            # Top 3 Artikel zurückgeben
            top_articles = [articles[i] for i in indices if i < len(articles)]
            
            print(f"  → Claude wählte: {result}")
            return top_articles[:3]
        
        except Exception as e:
            print(f"  ⚠️  Relevanz-Filter Fehler: {e}, nutze erste 3 News")
            return articles[:3]
    
    def _get_category_context(self, category: str) -> str:
        """Gibt kategorie-spezifischen Kontext"""
        contexts = {
            'allgemein': 'Fokus: Makroökonomie, große Unternehmen, globale Wirtschaftsereignisse',
            'finanzen': 'Fokus: Börsennachrichten, Aktien, Fonds, Finanzprodukte',
            'krypto': 'Fokus: Bitcoin, Ethereum, Blockchain, Krypto-Märkte, Regulation',
            'forex': 'Fokus: Währungspaare, Zentralbanken, Geldpolitik, Devisen',
            'tech': 'Fokus: Tech-Unternehmen mit Marktrelevanz, Disruption, IPOs',
            'rohstoffe': 'Fokus: Gold, Öl, Edelmetalle, Agrarrohstoffe, Energiemärkte'
        }
        return contexts.get(category, 'Fokus: Wirtschaftliche Relevanz')
    
    def filter_all_categories(self, news_dict: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Filtere alle Kategorien"""
        filtered = {}
        
        for category, articles in news_dict.items():
            print(f"Filtere {len(articles)} {category}-News auf Top 3...")
            filtered[category] = self.evaluate_relevance(articles, category)
        
        return filtered


if __name__ == "__main__":
    # Test
    filter = RelevanceFilter()
    
    test_articles = [
        {'title': 'Sparkassen-Einbruch in Gelsenkirchen', 'source': 'Test'},
        {'title': 'DAX erreicht neues Allzeithoch', 'source': 'Test'},
        {'title': 'Linke Partei streitet mit AfD', 'source': 'Test'},
        {'title': 'EZB senkt Leitzins um 0.25%', 'source': 'Test'},
        {'title': 'Microsoft übernimmt KI-Startup', 'source': 'Test'},
        {'title': 'Lokales Fest in München abgesagt', 'source': 'Test'},
    ]
    
    result = filter.evaluate_relevance(test_articles, 'allgemein')
    print("\nTop 3:")
    for article in result:
        print(f"- {article['title']}")