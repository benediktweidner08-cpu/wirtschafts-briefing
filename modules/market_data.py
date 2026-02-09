"""
Marktdaten-Modul mit yfinance
"""
import yfinance as yf
from typing import Dict, List
import yaml


class MarketData:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.symbols = self.config.get('market_symbols', {})
    
    def get_quote(self, symbol: str, name: str) -> Dict:
        """Hole Kursdaten für ein Symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='2d')
            
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            return {
                'name': name,
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_pct': change_pct,
                'arrow': '↑' if change >= 0 else '↓',
                'color': 'green' if change >= 0 else 'red'
            }
        
        except Exception as e:
            print(f"Fehler bei {symbol}: {e}")
            return None
    
    def get_all_markets(self) -> Dict[str, List[Dict]]:
        """Hole alle konfigurierten Marktdaten"""
        results = {}
        
        for category, items in self.symbols.items():
            category_data = []
            for item in items:
                quote = self.get_quote(item['symbol'], item['name'])
                if quote:
                    category_data.append(quote)
            results[category] = category_data
        
        return results
    
    def format_market_summary(self) -> str:
        """Formatiere Marktdaten für Email (Text)"""
        markets = self.get_all_markets()
        lines = []
        
        category_names = {
            'indices': 'Indizes',
            'crypto': 'Kryptowährungen',
            'commodities': 'Rohstoffe',
            'forex': 'Devisen'
        }
        
        for category, data in markets.items():
            if not data:
                continue
            
            lines.append(f"\n{category_names.get(category, category)}:")
            for item in data:
                lines.append(
                    f"  {item['name']}: {item['price']:.2f} "
                    f"{item['arrow']} {item['change_pct']:+.2f}%"
                )
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Test
    market = MarketData("../config.yaml")
    print(market.format_market_summary())
