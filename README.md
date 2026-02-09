# Wirtschafts-Briefing Generator 📊

Automatisches tägliches Email-Briefing mit Wirtschaftsnews und Marktdaten.

## Features

- ✅ RSS-Feeds von Handelsblatt, Manager Magazin, ZEIT, WELT
- ✅ Marktdaten: DAX, Dow Jones, S&P 500, Bitcoin, Gold, Silber, EUR/USD
- ✅ KI-gestützte Zusammenfassungen mit Claude
- ✅ Strukturiertes HTML-Email
- ✅ Kategorien: Allgemein, Finanzmärkte, Tech
- ✅ Automatischer Versand via GitHub Actions (täglich 20:00)

## Installation

### 1. Repository klonen
```bash
git clone <dein-repo>
cd wirtschafts-briefing
```

### 2. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 3. Umgebungsvariablen einrichten

Kopiere `.env.example` nach `.env`:
```bash
cp .env.example .env
```

Bearbeite `.env` und füge hinzu:

#### Outlook App-Passwort erstellen:
1. Gehe zu https://account.microsoft.com/security
2. Navigiere zu "Sicherheit" → "Erweiterte Sicherheitsoptionen"
3. Unter "App-Kennwörter" → "Neues App-Kennwort erstellen"
4. Kopiere das generierte Passwort in `.env`

#### Claude API Key:
1. Gehe zu https://console.anthropic.com/
2. Erstelle einen API Key
3. Kopiere ihn in `.env`

```env
EMAIL_PASSWORD=dein_16_stelliges_outlook_app_passwort
ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Konfiguration anpassen (optional)

Bearbeite `config.yaml` um:
- RSS-Feeds hinzuzufügen/zu entfernen
- Anzahl News pro Kategorie zu ändern
- Markt-Symbole anzupassen

## Lokaler Test

```bash
python main.py
```

Das Script wird:
1. RSS-Feeds parsen
2. Marktdaten abrufen
3. News mit Claude zusammenfassen
4. Email an dich senden

## GitHub Actions Setup (Automatischer täglicher Versand)

### 1. GitHub Repository erstellen

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/dein-username/wirtschafts-briefing.git
git push -u origin main
```

### 2. GitHub Secrets konfigurieren

Gehe zu deinem Repository → Settings → Secrets and variables → Actions

Füge folgende Secrets hinzu:
- `EMAIL_PASSWORD`: Dein Outlook App-Passwort
- `ANTHROPIC_API_KEY`: Dein Claude API Key

### 3. Workflow-Datei erstellen

Erstelle `.github/workflows/daily-briefing.yml`:

```yaml
name: Daily Economic Briefing

on:
  schedule:
    # Täglich um 20:00 Uhr MEZ (18:00 UTC)
    - cron: '0 18 * * *'
  
  # Manueller Trigger für Tests
  workflow_dispatch:

jobs:
  send-briefing:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install Dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run Briefing
      env:
        EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      run: |
        python main.py
```

### 4. Workflow testen

1. Gehe zu Actions → Daily Economic Briefing
2. Klicke "Run workflow" → "Run workflow"
3. Überprüfe dein Email-Postfach

### 5. Zeitzone anpassen (falls nötig)

Die Cron-Expression `0 18 * * *` bedeutet:
- 18:00 UTC = 19:00 MEZ (Winterzeit) = 20:00 MESZ (Sommerzeit)

Für genau 20:00 MEZ (Winterzeit):
```yaml
- cron: '0 19 * * *'  # 20:00 MEZ Winterzeit
```

## Projekt-Struktur

```
wirtschafts-briefing/
├── main.py                    # Hauptprogramm
├── config.yaml               # Konfiguration
├── requirements.txt          # Python Dependencies
├── .env                      # Secrets (NICHT committen!)
├── .env.example             # Template für .env
├── modules/
│   ├── rss_parser.py         # RSS-Feed Parser
│   ├── market_data.py        # Marktdaten (yfinance)
│   ├── summarizer.py         # Claude AI Zusammenfassung
│   └── email_sender.py       # Outlook SMTP
└── templates/
    └── email_template.html   # HTML Email-Layout
```

## Fehlerbehebung

### "ANTHROPIC_API_KEY nicht gefunden"
- Überprüfe `.env` Datei im Hauptverzeichnis
- Stelle sicher, dass keine Leerzeichen um `=` sind

### "SMTP Authentication Failed"
- Nutze App-Passwort, NICHT dein normales Outlook-Passwort
- 2FA muss aktiviert sein für App-Passwörter

### GitHub Actions schlägt fehl
- Überprüfe Secrets in Repository Settings
- Schaue in Actions → Workflow → Logs für Details

### Keine News gefunden
- RSS-Feeds könnten offline sein
- Zeitfilter anpassen in `config.yaml` (`news_hours_filter`)

## Anpassungen

### Mehr RSS-Feeds hinzufügen
Bearbeite `config.yaml`:
```yaml
rss_feeds:
  allgemein:
    - https://dein-neuer-feed.com/rss
```

### Andere Markt-Symbole
Suche Symbol auf https://finance.yahoo.com und füge hinzu:
```yaml
market_symbols:
  indices:
    - symbol: ^IXIC  # NASDAQ
      name: NASDAQ
```

### Email-Design ändern
Bearbeite `templates/email_template.html`

## Lizenz

Privat / Persönliche Nutzung
