"""
PDF-Generator für Wirtschafts-Briefing
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, List
from datetime import datetime
import yaml
import os


class PDFGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.pdf_path = self.config['output'].get('pdf_path', './briefings/')
        
        # Erstelle Ordner falls nicht vorhanden
        os.makedirs(self.pdf_path, exist_ok=True)
        
        # Styles definieren
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Erstelle custom Styles"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.section_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )
        
        self.headline_style = ParagraphStyle(
            'Headline',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#2C3E50')
        )
        
        self.source_style = ParagraphStyle(
            'Source',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            spaceAfter=8
        )
    
    def _format_market_data(self, market_data: Dict[str, List[Dict]]) -> List:
        """Formatiere Marktdaten für PDF"""
        elements = []
        
        category_names = {
            'indices': 'Indizes',
            'crypto': 'Kryptowährungen',
            'commodities': 'Rohstoffe',
            'forex': 'Devisen'
        }
        
        # Überschrift
        elements.append(Paragraph("Marktüberblick", self.section_style))
        
        # Erstelle Tabelle für alle Märkte
        table_data = []
        
        for category, items in market_data.items():
            if not items:
                continue
            
            # Kategorie-Überschrift
            table_data.append([
                Paragraph(f"<b>{category_names.get(category, category)}</b>", self.normal_style),
                '', ''
            ])
            
            # Marktdaten
            for item in items:
                color = 'green' if item['change'] >= 0 else 'red'
                table_data.append([
                    Paragraph(item['name'], self.normal_style),
                    Paragraph(f"{item['price']:.2f}", self.normal_style),
                    Paragraph(
                        f"<font color='{color}'>{item['arrow']} {item['change_pct']:+.2f}%</font>",
                        self.normal_style
                    )
                ])
        
        if table_data:
            table = Table(table_data, colWidths=[6*cm, 4*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2C3E50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0'))
            ]))
            elements.append(table)
        
        elements.append(Spacer(1, 0.5*cm))
        return elements
    
    def _format_news_item(self, article: Dict) -> List:
        """Formatiere einzelne News für PDF"""
        elements = []
        
        # Headline
        elements.append(Paragraph(article['headline'], self.headline_style))
        
        # Quelle
        elements.append(Paragraph(f"Quelle: {article['source']}", self.source_style))
        
        # Kernaussage
        elements.append(Paragraph(article['kernaussage'], self.normal_style))
        elements.append(Spacer(1, 0.2*cm))
        
        # Konsequenzen
        if article['konsequenzen']:
            elements.append(Paragraph("<b>Mögliche Konsequenzen:</b>", self.normal_style))
            for konsequenz in article['konsequenzen']:
                elements.append(Paragraph(f"• {konsequenz}", self.normal_style))
        
        elements.append(Spacer(1, 0.4*cm))
        return elements
    
    def generate_pdf(
        self,
        market_data: Dict,
        summarized_news: Dict[str, List[Dict]]
    ) -> str:
        """Generiere PDF und gebe Dateipfad zurück"""
        
        # Dateiname mit Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"wirtschafts-briefing_{timestamp}.pdf"
        filepath = os.path.join(self.pdf_path, filename)
        
        # PDF erstellen
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Titel
        now = datetime.now().strftime("%d.%m.%Y, %H:%M Uhr")
        story.append(Paragraph("Wirtschafts-Briefing", self.title_style))
        story.append(Paragraph(now, ParagraphStyle(
            'Date',
            parent=self.normal_style,
            alignment=TA_CENTER,
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )))
        story.append(Spacer(1, 0.8*cm))
        
        # Marktdaten
        story.extend(self._format_market_data(market_data))
        
        # News-Sektionen
        sections = {
            'allgemein': '🌍 Wirtschaft & Politik',
            'finanzen': '💰 Finanzmärkte',
            'krypto': '₿ Kryptowährungen',
            'forex': '💱 Forex & Devisen',
            'tech': '💻 Technologie',
            'rohstoffe': '🛢️ Rohstoffe'
        }
        
        for category, title in sections.items():
            articles = summarized_news.get(category, [])
            
            if not articles:
                continue
            
            # Sektion-Titel
            story.append(Paragraph(title, self.section_style))
            
            # News-Items
            for article in articles:
                story.extend(self._format_news_item(article))
        
        # Footer
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Automatisch generiert am {now}<br/>"
            "Quellen: Handelsblatt, Manager Magazin, ZEIT, WiWo, DER AKTIONÄR, "
            "BTC-ECHO, CoinDesk, FXStreet, Heise, t3n, Golem",
            ParagraphStyle(
                'Footer',
                parent=self.normal_style,
                fontSize=8,
                textColor=colors.HexColor('#999999'),
                alignment=TA_CENTER
            )
        ))
        
        # PDF generieren
        doc.build(story)
        
        print(f"✅ PDF erstellt: {filepath}")
        return filepath


if __name__ == "__main__":
    # Test
    generator = PDFGenerator("../config.yaml")
    
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
    
    filepath = generator.generate_pdf(test_market, test_news)
    print(f"PDF erstellt: {filepath}")