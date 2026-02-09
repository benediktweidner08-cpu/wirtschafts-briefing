"""
News-Zusammenfassung mit Claude API
"""
from anthropic import Anthropic
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class NewsSummarizer:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY nicht in .env gefunden")
        
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def summarize_article(self, article: Dict) -> Dict:
        """Fasse einen einzelnen Artikel zusammen"""
        
        prompt = f"""Fasse diese Wirtschaftsnachricht kompakt zusammen:

Titel: {article['title']}
Quelle: {article['source']}
Text: {article.get('summary', 'Kein Volltext verfügbar')}

Format deine Antwort EXAKT so:

HEADLINE: [Prägnante Überschrift in 5-8 Wörtern]

KERNAUSSAGE: [2-3 Sätze die das Wichtigste zusammenfassen]

KONSEQUENZEN:
• [Konkrete mögliche Folge 1]
• [Konkrete mögliche Folge 2]
• [Optional: Konkrete mögliche Folge 3]

Halte dich kurz und fokussiert. Nutze wirtschaftliche Fachbegriffe wo angebracht."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            summary_text = response.content[0].text
            
            # Parse die Antwort
            sections = self._parse_summary(summary_text)
            
            return {
                'original_title': article['title'],
                'headline': sections.get('headline', article['title']),
                'kernaussage': sections.get('kernaussage', ''),
                'konsequenzen': sections.get('konsequenzen', []),
                'source': article['source'],
                'link': article['link']
            }
        
        except Exception as e:
            print(f"Fehler bei Zusammenfassung: {e}")
            return {
                'original_title': article['title'],
                'headline': article['title'],
                'kernaussage': article.get('summary', '')[:300],
                'konsequenzen': [],
                'source': article['source'],
                'link': article['link']
            }
    
    def _parse_summary(self, text: str) -> Dict:
        """Parse die strukturierte Antwort von Claude"""
        sections = {
            'headline': '',
            'kernaussage': '',
            'konsequenzen': []
        }
        
        lines = text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('HEADLINE:'):
                sections['headline'] = line.replace('HEADLINE:', '').strip()
            elif line.startswith('KERNAUSSAGE:'):
                current_section = 'kernaussage'
                kern = line.replace('KERNAUSSAGE:', '').strip()
                if kern:
                    sections['kernaussage'] = kern
            elif line.startswith('KONSEQUENZEN:'):
                current_section = 'konsequenzen'
            elif line.startswith('•') or line.startswith('-'):
                if current_section == 'konsequenzen':
                    sections['konsequenzen'].append(line.lstrip('•-').strip())
            elif current_section == 'kernaussage' and not line.startswith('KONSEQUENZEN'):
                sections['kernaussage'] += ' ' + line
        
        return sections
    
    def summarize_all(self, news_dict: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Fasse alle News-Kategorien zusammen"""
        summarized = {}
        
        for category, articles in news_dict.items():
            print(f"Fasse {len(articles)} {category}-News zusammen...")
            summarized[category] = []
            
            for article in articles:
                summary = self.summarize_article(article)
                summarized[category].append(summary)
        
        return summarized


if __name__ == "__main__":
    # Test
    summarizer = NewsSummarizer()
    
    test_article = {
        'title': 'DAX erreicht neues Allzeithoch bei 20.500 Punkten',
        'summary': 'Der deutsche Leitindex DAX hat heute ein neues Rekordhoch erreicht...',
        'source': 'Handelsblatt',
        'link': 'https://example.com'
    }
    
    result = summarizer.summarize_article(test_article)
    print(f"Headline: {result['headline']}")
    print(f"Kernaussage: {result['kernaussage']}")
    print(f"Konsequenzen: {result['konsequenzen']}")
