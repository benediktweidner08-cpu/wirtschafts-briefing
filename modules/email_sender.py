"""
Email-Versand mit Outlook SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from datetime import datetime
import yaml
import os
from dotenv import load_dotenv

load_dotenv()


class EmailSender:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.smtp_server = self.config['email']['smtp_server']
        self.smtp_port = self.config['email']['smtp_port']
        self.sender = self.config['email']['sender']
        self.recipient = self.config['email']['recipient']
        self.password = os.getenv('EMAIL_PASSWORD')
        
        if not self.password:
            raise ValueError("EMAIL_PASSWORD nicht in .env gefunden")
        
        # Template laden
        with open('templates/email_template.html', 'r', encoding='utf-8') as f:
            self.template = f.read()
    
    def _format_market_data(self, market_data: Dict[str, List[Dict]]) -> str:
        """Formatiere Marktdaten für HTML"""
        html = ""
        
        category_names = {
            'indices': 'Indizes',
            'crypto': 'Kryptowährungen',
            'commodities': 'Rohstoffe',
            'forex': 'Devisen'
        }
        
        for category, items in market_data.items():
            if not items:
                continue
            
            html += f'<div class="market-category">'
            html += f'<h3>{category_names.get(category, category)}</h3>'
            
            for item in items:
                color_class = 'positive' if item['change'] >= 0 else 'negative'
                html += f'<div class="market-item">'
                html += f'<span class="market-name">{item["name"]}:</span> '
                html += f'<span class="{color_class}">'
                html += f'{item["price"]:.2f} {item["arrow"]} {item["change_pct"]:+.2f}%'
                html += f'</span>'
                html += f'</div>'
            
            html += '</div>'
        
        return html
    
    def _format_news_item(self, article: Dict) -> str:
        """Formatiere einzelne News für HTML"""
        html = '<div class="news-item">'
        html += f'<div class="news-headline">{article["headline"]}</div>'
        html += f'<div class="news-source">Quelle: {article["source"]}</div>'
        html += f'<div class="news-summary">{article["kernaussage"]}</div>'
        
        if article['konsequenzen']:
            html += '<div class="consequences">'
            html += '<strong>Mögliche Konsequenzen:</strong>'
            html += '<ul>'
            for konsequenz in article['konsequenzen']:
                html += f'<li>{konsequenz}</li>'
            html += '</ul>'
            html += '</div>'
        
        html += f'<a href="{article["link"]}" class="read-more">Weiterlesen →</a>'
        html += '</div>'
        
        return html
    
    def _format_news_section(self, articles: List[Dict]) -> str:
        """Formatiere alle News einer Kategorie"""
        return '\n'.join(self._format_news_item(article) for article in articles)
    
    def create_email_content(
        self, 
        market_data: Dict,
        summarized_news: Dict[str, List[Dict]]
    ) -> str:
        """Erstelle HTML-Content für Email"""
        
        now = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")
        
        content = self.template
        content = content.replace('{{ date }}', now)
        content = content.replace('{{ market_data }}', self._format_market_data(market_data))
        content = content.replace('{{ allgemein_news }}', self._format_news_section(summarized_news.get('allgemein', [])))
        content = content.replace('{{ finanzen_news }}', self._format_news_section(summarized_news.get('finanzen', [])))
        content = content.replace('{{ krypto_news }}', self._format_news_section(summarized_news.get('krypto', [])))
        content = content.replace('{{ forex_news }}', self._format_news_section(summarized_news.get('forex', [])))
        content = content.replace('{{ tech_news }}', self._format_news_section(summarized_news.get('tech', [])))
        content = content.replace('{{ rohstoffe_news }}', self._format_news_section(summarized_news.get('rohstoffe', [])))
        
        return content
    
    def send_briefing(
        self,
        market_data: Dict,
        summarized_news: Dict[str, List[Dict]]
    ):
        """Sende das Briefing per Email"""
        
        # Email erstellen
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'📊 Wirtschafts-Briefing – {datetime.now().strftime("%d.%m.%Y")}'
        msg['From'] = self.sender
        msg['To'] = self.recipient
        
        # HTML Content
        html_content = self.create_email_content(market_data, summarized_news)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Senden
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            print(f"✅ Briefing erfolgreich an {self.recipient} gesendet")
        
        except Exception as e:
            print(f"❌ Fehler beim Email-Versand: {e}")
            raise


if __name__ == "__main__":
    # Test mit Dummy-Daten
    sender = EmailSender("../config.yaml")
    
    test_market = {
        'indices': [
            {'name': 'DAX', 'price': 20345.67, 'change': 123.45, 'change_pct': 0.61, 'arrow': '↑'}
        ]
    }
    
    test_news = {
        'allgemein': [
            {
                'headline': 'Test Headline',
                'kernaussage': 'Dies ist ein Test.',
                'konsequenzen': ['Konsequenz 1', 'Konsequenz 2'],
                'source': 'Test-Quelle',
                'link': 'https://example.com'
            }
        ]
    }
    
    content = sender.create_email_content(test_market, test_news)
    print("Email-Content erstellt (Test)")
