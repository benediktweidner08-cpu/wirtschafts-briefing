# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Automated weekly economic briefing system (runs **Tuesdays only**). Fetches German-language financial news from RSS feeds, filters and summarizes it with Claude AI, fetches live market data, and delivers a briefing via HTML email and/or PDF.

## Running the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY and EMAIL_PASSWORD

# Run the briefing
python main.py
```

**Important:** `main.py` exits early if today is not Tuesday (`datetime.now().weekday() != 1`). To test on other days, temporarily comment out lines 25–28 in `main.py`.

To skip email sending or PDF generation during testing, set in `config.yaml`:
```yaml
output:
  send_email: false
  generate_pdf: false
```

## Architecture

The pipeline in `main.py` runs 7 sequential steps:

```
RSS Feeds → rss_parser (6/category) → relevance_filter (top 3/category, Claude AI)
                                                    ↓
                                           summarizer (Claude AI)
                                                    ↓
yfinance → market_data ──────────────→ email_sender + pdf_generator
```

### Modules

| Module | Role |
|---|---|
| `modules/rss_parser.py` | Fetches RSS feeds, deduplicates, filters to last 24h |
| `modules/relevance_filter.py` | Uses Claude to score and select top 3 articles per category |
| `modules/summarizer.py` | Uses Claude to produce structured HEADLINE / KERNAUSSAGE / KONSEQUENZEN summaries |
| `modules/market_data.py` | Fetches price quotes via yfinance; returns price, change, arrow, color |
| `modules/email_sender.py` | Fills `templates/email_template.html` and sends via Gmail SMTP (TLS port 587) |
| `modules/pdf_generator.py` | Builds PDF via reportlab into `./briefings/` |

### Configuration

- **`config.yaml`** — RSS feed URLs, market symbols (yfinance format), email addresses, news counts, time filter window
- **`.env`** — `ANTHROPIC_API_KEY` and `EMAIL_PASSWORD` (Gmail App Password); never committed

### AI Model

All Claude calls use **`claude-haiku-4-5-20251001`**. This is set in:
- `modules/summarizer.py` (line ~19)
- `modules/relevance_filter.py` (line ~18)

### News Categories

Six categories flow through the entire pipeline: `allgemein`, `finanzen`, `krypto`, `forex`, `tech`, `rohstoffe`.

### Summarizer Output Format

Claude is prompted to return a fixed structure parsed by `_parse_summary()`:
```
HEADLINE: [5-8 word rewrite]
KERNAUSSAGE: [2-3 sentence summary]
KONSEQUENZEN:
• [implication 1]
• [implication 2]
• [implication 3]
```

### PDF Output

PDFs are saved to `./briefings/wirtschafts-briefing_YYYY-MM-DD_HH-MM.pdf`. HTML characters in content are escaped via `xml.sax.saxutils.escape()` before being passed to reportlab.

## Deployment

GitHub Actions workflow runs daily at 18:00 UTC (≈ 20:00 CET). Secrets `ANTHROPIC_API_KEY` and `EMAIL_PASSWORD` must be set in the repository's Actions secrets. The Tuesday guard in `main.py` ensures the briefing is only sent on Tuesdays even though the workflow runs daily.
