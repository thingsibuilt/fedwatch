# FedWatch 🏛️

**Real-Time Economic Intelligence Platform**

> The Fed operates with 2-4 week data lags. Markets price ahead of official data. Shouldn't we?

## The Problem

- Official economic data lags 2-4 weeks
- Bloomberg terminals cost $25k+/year
- Alternative data is fragmented and expensive

## The Solution

FedWatch aggregates real-time alternative data sources to provide faster economic signals.

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Scrapers   │───▶│    API      │───▶│  Frontend   │
│  (Python)   │    │  (FastAPI)  │    │  (React)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Data Sources

### Official (Current)
- BLS - Unemployment, CPI, PCE
- FRED - Historical data
- Federal Reserve - Interest rates

### Alternative (Coming Soon)
- **Indeed API** - Job postings by category
- **Google Trends** - Economic search signals
- **Realtor.com** - Housing market data
- **News API** - Sentiment analysis
- **Plaid** - Consumer spending

## Quick Start

### 1. Clone & Install

```bash
cd fedwatch
pip install -r requirements.txt  # Python deps
npm install                     # Node deps
```

### 2. Run API

```bash
python api.py
# API runs at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 3. Run Scraper

```bash
# For Indeed (requires Indeed Publisher API key)
export INDEED_API_KEY="your_key"
python scrapers/indeed_scraper.py

# For Google Trends
python scrapers/google_trends.py
```

### 4. Frontend

```bash
cd frontend
npm run dev
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/employment` | Unemployment, payrolls |
| `GET /api/v1/inflation` | CPI, PCE, PPI |
| `GET /api/v1/signals` | Real-time alternative data |
| `GET /api/v1/health` | Economic health score |

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL + TimescaleDB
- **Streaming**: Kafka
- **Scrapers**: Python (BeautifulSoup, Scrapy)
- **Frontend**: React, Next.js, Chart.js

## Contributing

Open source! PRs welcome.

## Disclaimer

NOT FINANCIAL ADVICE. For educational purposes only.

---

Built with ❤️ by Pixel & Ryan
