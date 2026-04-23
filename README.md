# BC Terminal

A personal equity dashboard built with Streamlit. Tracks a portfolio of
holdings, shows live quotes for a watchlist by sector, and lets you chart
and review fundamentals for any ticker.

## Features

- **Live market overview** — major indices (S&P 500, Nasdaq, Dow, Russell 2000,
  VIX, 10Y yield) at the top.
- **Fund holdings** with live market value, unrealized P&L, and weight.
  Positions are computed from a simple trade log using average-cost accounting.
- **Sector watchlists** — Banks, Asset Managers, Insurance, Payments.
- **Charting** — candlestick, line, or area, with volume subplot. Supports any
  ticker: sector dropdown or free-text input (e.g. `NVDA`, `^GSPC`, `BTC-USD`).
- **Fundamentals grid** — 16 metrics including P/E, ROE, market cap, margins,
  52-week range.
- **Optional password gate** for deployed versions.

## Run locally

Requirements: Python 3.9+ (tested on 3.14).

```bash
python -m pip install -r requirements.txt
python -m streamlit run terminal_dashboard.py
```

The app opens at `http://localhost:8501`.

## Edit your holdings

All trades live in the `FUND_TRADES` list near the top of `terminal_dashboard.py`.
Add a new line every time you trade:

```python
FUND_TRADES = [
    {"date": "2026-04-21", "ticker": "FCFS", "action": "BUY",  "shares": 15, "price": 206.50},
    {"date": "2026-05-03", "ticker": "FCFS", "action": "BUY",  "shares": 10, "price": 210.00},
    {"date": "2026-06-10", "ticker": "FCFS", "action": "SELL", "shares": 5,  "price": 215.00},
]
```

Positions and weighted-average cost basis are computed automatically.

## Deploy to Streamlit Cloud

1. **Create a GitHub repository.** Sign up at https://github.com if needed.
   Make a new repo (can be public — the password gate protects your data).
2. **Upload these files to the repo:**
   - `terminal_dashboard.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`
   
   Do NOT upload `secrets.toml` or `.streamlit/secrets.toml` — those contain
   your password and must stay local.
3. **Go to https://share.streamlit.io** and sign in with GitHub.
4. Click **New app**, pick your repo, choose `terminal_dashboard.py` as the
   main file, and click **Deploy**. You'll get a URL like
   `bc-terminal.streamlit.app` (you can customize the subdomain).
5. **Set your password.** In the app's dashboard on Streamlit Cloud, click
   **Settings** > **Secrets**. Paste this, with a real password:
   ```toml
   password = "your-strong-password-here"
   ```
   Save. The app will restart and require that password to view.

## Data source

Market data is pulled from Yahoo Finance via the `yfinance` library. Results
are cached for 60 seconds (prices) and 5 minutes (fundamentals) to avoid
hitting rate limits. If the library breaks when Yahoo changes their API,
update it with `python -m pip install --upgrade yfinance`.

## Files

| File | Purpose |
|------|---------|
| `terminal_dashboard.py` | The Streamlit app |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Keeps secrets out of the repo |
| `secrets.toml.example` | Template for local password setup |
| `README.md` | This file |
