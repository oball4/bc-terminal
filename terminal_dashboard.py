import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Knight Terminal",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# FUND TRADES — LOG EACH BUY/SELL HERE
# =========================
# Format:
#   {"date": "YYYY-MM-DD", "ticker": "XXX", "action": "BUY"|"SELL", "shares": N, "price": P.PP}
FUND_TRADES = [
    {"date": "2026-04-21", "ticker": "FCFS", "action": "BUY", "shares": 15, "price": 206.50},
]


def aggregate_trades(trades):
    """Roll up a trade log into current positions (average-cost method)."""
    positions = {}
    for tr in trades:
        t = tr["ticker"]
        shares, price = tr["shares"], tr["price"]
        action = tr.get("action", "BUY").upper()
        pos = positions.setdefault(t, {"shares": 0, "total_cost": 0.0})
        if action == "BUY":
            pos["shares"] += shares
            pos["total_cost"] += shares * price
        elif action == "SELL":
            if pos["shares"] > 0:
                avg = pos["total_cost"] / pos["shares"]
                pos["shares"] -= shares
                pos["total_cost"] -= shares * avg
    return [
        {"ticker": t, "shares": p["shares"], "cost_basis": p["total_cost"] / p["shares"]}
        for t, p in positions.items() if p["shares"] > 0
    ]


FUND_HOLDINGS = aggregate_trades(FUND_TRADES)

# =========================
# SECTOR & INDUSTRY ETFs
# =========================
# Standard proxies for broad-market performance tracking. SPDR Select Sector
# ETFs for S&P 500 sectors, plus popular sub-industry ETFs.
SECTOR_ETFS = {
    "Technology":             "XLK",
    "Financials":             "XLF",
    "Health Care":            "XLV",
    "Energy":                 "XLE",
    "Consumer Discretionary": "XLY",
    "Consumer Staples":       "XLP",
    "Industrials":            "XLI",
    "Materials":              "XLB",
    "Utilities":              "XLU",
    "Real Estate":            "XLRE",
    "Communication Services": "XLC",
}

INDUSTRY_ETFS = {
    # Technology
    "Semiconductors":         "SOXX",
    "Software":               "IGV",
    "Cybersecurity":          "CIBR",
    "Internet":               "FDN",
    # Financials
    "Banks":                  "KBE",
    "Regional Banks":         "KRE",
    "Insurance":              "KIE",
    # Health Care
    "Biotech":                "XBI",
    "Medical Devices":        "IHI",
    "Pharma":                 "IHE",
    # Energy
    "Oil & Gas E&P":          "XOP",
    "Oil Services":           "OIH",
    "Clean Energy":           "ICLN",
    # Consumer
    "Homebuilders":           "XHB",
    "Retail":                 "XRT",
    # Industrials
    "Aerospace & Defense":    "ITA",
    "Transportation":         "IYT",
    # Materials
    "Gold Miners":            "GDX",
    "Metals & Mining":        "XME",
    # Commodities
    "Gold":                   "GLD",
    "Crude Oil":              "USO",
    # Fixed Income
    "20Y Treasuries":         "TLT",
    "High Yield Bonds":       "HYG",
    # International
    "Emerging Markets":       "EEM",
    "China":                  "MCHI",
    "Europe":                 "VGK",
}

# =========================
# STYLE — LIGHT MODE / NAVY ACCENT
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp {
    background-color: #ffffff;
    color: #111827;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

p, label,
.stMarkdown p, .stMarkdown li,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: #111827 !important;
}

h1, h2, h3, h4, h5 {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: #111827 !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}

[data-testid="stSidebar"] {
    background-color: #f9fafb;
    border-right: 1px solid #e5e7eb;
}

[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] p {
    color: #6b7280 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 22px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}

[data-testid="stTextInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid #e5e7eb !important;
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* TABS — custom styling to match theme */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 28px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    padding: 10px 4px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    letter-spacing: 0.02em;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #0a1938 !important;
    border-bottom: 2px solid #2563eb !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none;
}

/* Banner */
.banner {
    background: linear-gradient(135deg, #0a1938 0%, #162a4f 55%, #0a1938 100%);
    padding: 22px 28px;
    margin: -1rem -1rem 24px -1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}
.banner::after {
    content: '';
    position: absolute;
    left: 0; right: 0; bottom: -1px;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
}
.banner .title {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 22px;
    color: #ffffff;
    letter-spacing: -0.01em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.banner .title .mark {
    color: #60a5fa;
    font-weight: 300;
    font-size: 26px;
    line-height: 1;
}
.banner .title .sub {
    color: #cbd5e1;
    font-weight: 400;
    margin-left: 6px;
}
.banner .meta {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: #9ca3af;
    text-align: right;
}
.banner .meta .date {
    color: #e5e7eb;
    font-weight: 500;
}

/* Section headers */
.panel-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 12px;
    color: #111827;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 0 0 8px 0;
    margin: 24px 0 12px 0;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #2563eb;
}

.kicker {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    color: #2563eb;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 2px;
}

/* News items */
.news-item {
    border-bottom: 1px solid #f3f4f6;
    padding: 14px 0;
}
.news-item:last-child { border-bottom: none; }
.news-item .headline {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 15px;
    color: #111827;
    text-decoration: none;
    line-height: 1.4;
    display: block;
    margin-bottom: 4px;
}
.news-item .headline:hover {
    color: #2563eb;
    text-decoration: underline;
}
.news-item .meta {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #6b7280;
}
.news-item .meta .publisher {
    color: #2563eb;
    font-weight: 500;
}

/* Keep sidebar-collapse button visible */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background-color: transparent; }
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: block !important;
    z-index: 999999 !important;
}

hr { border: none; border-top: 1px solid #e5e7eb; margin: 16px 0; }
</style>
""", unsafe_allow_html=True)


# =========================
# OPTIONAL PASSWORD GATE
# =========================
def _configured_password():
    try:
        return st.secrets.get("password", None)
    except Exception:
        return None


_password = _configured_password()
if _password and not st.session_state.get("authenticated"):
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("### Knight Terminal")
        st.markdown("Enter password to continue.")
        pwd = st.text_input("Password", type="password", label_visibility="collapsed")
        if pwd:
            if pwd == _password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")
    st.stop()


# =========================
# HELPERS
# =========================
try:
    from curl_cffi import requests as curl_requests
    _HAS_CURL_CFFI = True
except ImportError:
    _HAS_CURL_CFFI = False


@st.cache_resource(show_spinner=False)
def get_session():
    if _HAS_CURL_CFFI:
        return curl_requests.Session(impersonate="chrome")
    return None


def fmt_big(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "—"
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "—"
    for div, suf in [(1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(n) >= div:
            return f"{n/div:.2f}{suf}"
    return f"{n:.2f}"


def fmt_pct(v):
    if v is None or pd.isna(v):
        return "—"
    return f"{v * 100:.2f}%"


def fmt_num(v, digits=2):
    if v is None or pd.isna(v):
        return "—"
    try:
        return f"{float(v):.{digits}f}"
    except (TypeError, ValueError):
        return "—"


@st.cache_data(ttl=600, show_spinner=False)
def get_history(ticker, period="1d", interval="1d"):
    try:
        return yf.Ticker(ticker, session=get_session()).history(
            period=period, interval=interval
        )
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=900, show_spinner=False)
def get_history_from(ticker, start_date):
    try:
        return yf.Ticker(ticker, session=get_session()).history(start=start_date)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_info(ticker):
    try:
        return yf.Ticker(ticker, session=get_session()).info or {}
    except Exception:
        return {}


def color_signed(val):
    try:
        v = float(
            str(val).replace("%", "").replace("+", "")
            .replace("$", "").replace(",", "")
        )
        return "color: #059669" if v >= 0 else "color: #dc2626"
    except Exception:
        return ""


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_macro_news(limit=10):
    """Pull recent headlines from macro tickers, dedupe by title, sort by recency.

    Skips content-mill / AI-generated publishers so the feed stays clean.
    """
    # Publishers whose output is heavily AI-generated, templated, or low-quality.
    # Match is case-insensitive substring — e.g. "Zacks Investment Research" matches "zacks".
    blocklist = {
        "motley fool",
        "insider monkey",
        "zacks",
        "benzinga",
        "24/7 wall st",
        "investorplace",
        "tipranks",
        "gurufocus",
        "valuewalk",
        "simply wall st",
        "stocknews",
        "validea",
        "stocktwits",
    }

    def is_blocked(publisher):
        if not publisher:
            return False
        p = str(publisher).lower()
        return any(b in p for b in blocklist)

    macro_tickers = ["^GSPC", "^IXIC", "^DJI", "^TNX"]
    items, seen = [], set()
    for t in macro_tickers:
        try:
            raw = yf.Ticker(t, session=get_session()).news or []
        except Exception:
            raw = []
        for it in raw:
            # yfinance news schema has changed over versions — handle both
            content = it.get("content", it)
            title = content.get("title") or it.get("title")
            if not title or title in seen:
                continue

            canon = content.get("canonicalUrl")
            url = ((canon.get("url") if isinstance(canon, dict) else None)
                   or content.get("link") or it.get("link") or "")

            prov = content.get("provider")
            publisher = ((prov.get("displayName") if isinstance(prov, dict) else None)
                         or it.get("publisher") or "—")

            # Skip blocked publishers
            if is_blocked(publisher):
                continue

            seen.add(title)

            pub_time = (content.get("pubDate") or content.get("displayTime")
                        or it.get("providerPublishTime"))

            items.append({
                "title": title, "url": url,
                "publisher": publisher, "pub_time": pub_time,
            })

    def _ts(item):
        t = item.get("pub_time")
        if isinstance(t, (int, float)):
            return float(t)
        if isinstance(t, str):
            try:
                return pd.Timestamp(t).timestamp()
            except Exception:
                return 0.0
        return 0.0

    items.sort(key=_ts, reverse=True)
    return items[:limit]


def format_news_time(pub_time):
    """Relative time for fresh news, absolute date for older."""
    if not pub_time:
        return ""
    try:
        if isinstance(pub_time, (int, float)):
            dt = pd.Timestamp(pub_time, unit="s", tz="UTC")
        else:
            dt = pd.Timestamp(pub_time)
            if dt.tz is None:
                dt = dt.tz_localize("UTC")
        now = pd.Timestamp.now(tz="UTC")
        delta = (now - dt).total_seconds()
        if delta < 3600:
            return f"{int(delta/60)}m ago"
        if delta < 86400:
            return f"{int(delta/3600)}h ago"
        if delta < 7 * 86400:
            return f"{int(delta/86400)}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return ""


def compute_portfolio_history(trades):
    """Daily market value timeline for the portfolio, vs cumulative cost basis."""
    if not trades:
        return pd.DataFrame()
    trades_sorted = sorted(trades, key=lambda t: t["date"])
    start = trades_sorted[0]["date"]
    tickers = sorted({t["ticker"] for t in trades})

    price_series = {}
    for t in tickers:
        hist = get_history_from(t, start)
        if hist.empty:
            continue
        s = hist["Close"].copy()
        s.index = s.index.tz_localize(None).normalize()
        price_series[t] = s

    if not price_series:
        return pd.DataFrame()

    all_dates = sorted(set().union(*(s.index for s in price_series.values())))
    records = []
    for date in all_dates:
        total_value, total_cost = 0.0, 0.0
        for ticker in tickers:
            shares, cost = 0, 0.0
            for tr in trades:
                trade_dt = pd.Timestamp(tr["date"]).normalize()
                if trade_dt > date or tr["ticker"] != ticker:
                    continue
                if tr["action"].upper() == "BUY":
                    shares += tr["shares"]
                    cost += tr["shares"] * tr["price"]
                elif tr["action"].upper() == "SELL":
                    if shares > 0:
                        avg = cost / shares
                        shares -= tr["shares"]
                        cost -= tr["shares"] * avg
            if shares <= 0:
                continue
            series = price_series.get(ticker)
            if series is None:
                continue
            if date in series.index:
                price = series.loc[date]
            else:
                prior = series[series.index <= date]
                if prior.empty:
                    continue
                price = prior.iloc[-1]
            total_value += shares * price
            total_cost += cost
        if total_value > 0:
            records.append({"Date": date, "Value": total_value, "Cost": total_cost})

    return pd.DataFrame(records)


def compute_returns_from_series(close_series):
    """Compute 1D/1W/1M/3M/YTD/1Y returns from a Close price Series.

    Uses trading-day offsets: ~5/22/63 for week/month/3-month. YTD uses
    the first trading day of the current year.
    """
    out = {"Last": None, "1D": None, "1W": None, "1M": None,
           "3M": None, "YTD": None, "1Y": None}
    if close_series is None or close_series.empty or len(close_series) < 2:
        return out
    last = float(close_series.iloc[-1])
    out["Last"] = last

    def _ret(offset):
        if len(close_series) > offset:
            ref = float(close_series.iloc[-1 - offset])
            if ref > 0:
                return (last - ref) / ref * 100
        return None

    out["1D"] = _ret(1)
    out["1W"] = _ret(5)
    out["1M"] = _ret(21)
    out["3M"] = _ret(63)

    # YTD — from first trading day of current year
    current_year = close_series.index[-1].year
    ytd_slice = close_series[close_series.index.year == current_year]
    if len(ytd_slice) >= 2:
        ref = float(ytd_slice.iloc[0])
        if ref > 0:
            out["YTD"] = (last - ref) / ref * 100

    # 1Y — use earliest point in the series (assumes period="1y")
    ref = float(close_series.iloc[0])
    if ref > 0:
        out["1Y"] = (last - ref) / ref * 100

    return out


def build_performance_table(ticker_map):
    """Build a performance DataFrame for a dict of {display_name: ticker}."""
    rows = []
    for name, ticker in ticker_map.items():
        hist = get_history(ticker, period="1y")
        if hist.empty:
            rows.append({"Name": name, "Ticker": ticker, "Last": None,
                         "1D": None, "1W": None, "1M": None, "3M": None,
                         "YTD": None, "1Y": None})
            continue
        r = compute_returns_from_series(hist["Close"])
        rows.append({"Name": name, "Ticker": ticker, **r})
    return pd.DataFrame(rows)


def format_and_style_perf(df):
    """Format the performance DataFrame for display and apply green/red coloring."""
    d = df.copy()
    d["Last"] = d["Last"].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "—")
    for col in ["1D", "1W", "1M", "3M", "YTD", "1Y"]:
        d[col] = d[col].apply(lambda x: f"{x:+.2f}%" if pd.notna(x) else "—")
    d = d.rename(columns={
        "1D": "1D %", "1W": "1W %", "1M": "1M %",
        "3M": "3M %", "YTD": "YTD %", "1Y": "1Y %",
    })
    pct_cols = ["1D %", "1W %", "1M %", "3M %", "YTD %", "1Y %"]
    return (
        d.style
        .set_properties(**{
            "background-color": "#ffffff",
            "color": "#111827",
            "font-family": "JetBrains Mono, monospace",
            "font-size": "13px",
        })
        .map(color_signed, subset=pct_cols)
    )


@st.cache_data(ttl=600, show_spinner=False)
def generate_market_summary():
    """Compose a one-paragraph market summary from live data.

    NOT an LLM-generated summary — just templated prose derived from price moves
    across indices, sectors, rates, and commodities. Describes WHAT moved,
    not WHY. Refreshes every 10 minutes.
    """
    def _move(ticker):
        hist = get_history(ticker, period="5d")
        if hist.empty or len(hist) < 2:
            return None
        last = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2])
        if prev == 0:
            return None
        return {"price": last, "pct": (last - prev) / prev * 100,
                "chg": last - prev}

    sp = _move("^GSPC")
    if not sp:
        return None

    nasdaq = _move("^IXIC")
    dow = _move("^DJI")
    rty = _move("^RUT")
    vix = _move("^VIX")
    ten_yr = _move("^TNX")
    gold = _move("GLD")
    oil = _move("USO")

    # Sector rotation (1-day)
    sector_moves = []
    for name, ticker in SECTOR_ETFS.items():
        m = _move(ticker)
        if m:
            sector_moves.append((name, m["pct"]))
    sector_moves.sort(key=lambda x: x[1], reverse=True)

    # S&P direction verb — scaled to magnitude for natural prose
    def _sp_verb(pct):
        if pct >= 1.5:  return "surged"
        if pct >= 0.5:  return "climbed"
        if pct >= 0.1:  return "edged higher"
        if pct > -0.1:  return "finished little changed"
        if pct > -0.5:  return "slipped"
        if pct > -1.5:  return "declined"
        return "tumbled"

    verb = _sp_verb(sp["pct"])
    if abs(sp["pct"]) < 0.1:
        lead = (f"The S&P 500 {verb} at {sp['price']:,.0f}, "
                f"{'up' if sp['pct'] >= 0 else 'down'} {abs(sp['pct']):.2f}%")
    else:
        lead = f"The S&P 500 {verb} {abs(sp['pct']):.2f}% to {sp['price']:,.0f}"

    # Sector leadership
    sector_sentence = ""
    if sector_moves:
        leaders = [s for s in sector_moves[:2] if s[1] > 0]
        laggards = [s for s in sector_moves[-2:] if s[1] < 0]
        if leaders and laggards:
            L = " and ".join(n for n, _ in leaders)
            G = " and ".join(n for n, _ in laggards)
            sector_sentence = f"{L} led the gainers while {G} lagged."
        elif leaders:
            L = " and ".join(n for n, _ in leaders)
            sector_sentence = f"{L} led broad sector gains."
        elif laggards:
            G = " and ".join(n for n, _ in laggards)
            sector_sentence = f"{G} lagged across a down session."

    # Other benchmarks
    other_parts = []
    if nasdaq:
        v = "added" if nasdaq["pct"] >= 0 else "lost"
        other_parts.append(f"the Nasdaq {v} {abs(nasdaq['pct']):.2f}%")
    if dow:
        v = "gained" if dow["pct"] >= 0 else "shed"
        other_parts.append(f"the Dow {v} {abs(dow['chg']):.0f} points")
    if rty:
        v = "rose" if rty["pct"] >= 0 else "fell"
        other_parts.append(f"small caps {v} {abs(rty['pct']):.2f}%")
    other_sentence = (f"Among major benchmarks, {'; '.join(other_parts)}."
                      if other_parts else "")

    # Rates / vol / commodities — only mention notable commodity moves
    macro_parts = []
    if ten_yr:
        v = "rose" if ten_yr["pct"] >= 0 else "eased"
        macro_parts.append(f"the 10-year Treasury yield {v} to {ten_yr['price']:.2f}%")
    if vix:
        v = "climbed" if vix["pct"] >= 0 else "eased"
        macro_parts.append(f"the VIX {v} to {vix['price']:.2f}")
    if gold and abs(gold["pct"]) >= 0.5:
        d = "higher" if gold["pct"] >= 0 else "lower"
        macro_parts.append(f"gold moved {d} by {abs(gold['pct']):.2f}%")
    if oil and abs(oil["pct"]) >= 1.0:
        d = "higher" if oil["pct"] >= 0 else "lower"
        macro_parts.append(f"crude oil traded {d} by {abs(oil['pct']):.2f}%")
    macro_sentence = (f"Elsewhere, {'; '.join(macro_parts)}."
                      if macro_parts else "")

    parts = [lead + ".", sector_sentence, other_sentence, macro_sentence]
    return " ".join(p for p in parts if p)


# =========================
# TOP BANNER
# =========================
today = datetime.now()
st.markdown(
    f"""
    <div class="banner">
        <div class="title">
            <span class="mark">■</span>
            <span>Knight Terminal</span>
            <span class="sub">Equity Dashboard</span>
        </div>
        <div class="meta">
            <div class="date">{today.strftime('%A, %B %d, %Y')}</div>
            <div>{today.strftime('%H:%M:%S')} · Market Data</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# SIDEBAR (applies to Markets tab)
# =========================
st.sidebar.markdown('<div class="panel-title">Sector</div>', unsafe_allow_html=True)
subsectors = {
    "Banks":          ["JPM", "BAC", "WFC", "C", "GS", "MS"],
    "Asset Managers": ["BLK", "TROW", "KKR", "APO", "BX"],
    "Insurance":      ["AIG", "ALL", "MET", "PRU", "TRV"],
    "Payments":       ["V", "MA", "PYPL", "AXP", "COF"],
}
selected_sector = st.sidebar.radio("Subsector", list(subsectors.keys()))
tickers = subsectors[selected_sector]

st.sidebar.markdown('<div class="panel-title">Chart</div>', unsafe_allow_html=True)
period = st.sidebar.select_slider(
    "Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="6mo"
)
chart_type = st.sidebar.radio("Chart Type", ["Candlestick", "Line", "Area"])

# =========================
# TABS
# =========================
tab_markets, tab_portfolio, tab_industries = st.tabs(["Markets", "Portfolio", "Industries"])

# =========================================================================
# MARKETS TAB
# =========================================================================
with tab_markets:
    # ---- Daily Market Summary ----
    summary = generate_market_summary()
    if summary:
        ts = datetime.now().strftime("%b %d, %Y · %I:%M %p")
        st.markdown(
            f"""
            <div style="border-left: 3px solid #2563eb; padding: 16px 22px;
                        background: #f9fafb; margin: 4px 0 28px 0;">
                <div style="font-family: 'Inter', sans-serif; font-size: 11px;
                            color: #2563eb; letter-spacing: 0.12em;
                            text-transform: uppercase; margin-bottom: 10px;
                            font-weight: 600;">
                    Today's Market &nbsp;·&nbsp; {ts}
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 15px;
                            color: #111827; line-height: 1.65;">
                    {summary}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Global Indices ----
    st.markdown('<div class="panel-title">Markets</div>', unsafe_allow_html=True)
    indices = {
        "S&P 500":      "^GSPC",
        "Nasdaq":       "^IXIC",
        "Dow Jones":    "^DJI",
        "Russell 2000": "^RUT",
        "VIX":          "^VIX",
        "10Y Yield":    "^TNX",
    }
    cols = st.columns(len(indices))
    for i, (name, ticker) in enumerate(indices.items()):
        data = get_history(ticker, period="5d")
        if data.empty:
            continue
        price = data["Close"].iloc[-1]
        prev = data["Close"].iloc[-2] if len(data) >= 2 else data["Open"].iloc[-1]
        pct = (price - prev) / prev * 100
        cols[i].metric(label=name, value=f"{price:,.2f}", delta=f"{pct:+.2f}%")

    # ---- Sector Quotes + Chart ----
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown(
            f'<div class="kicker">Sector</div>'
            f'<div class="panel-title">{selected_sector}</div>',
            unsafe_allow_html=True,
        )
        rows = []
        for t in tickers:
            hist = get_history(t, period="5d")
            if hist.empty:
                continue
            price = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-2] if len(hist) >= 2 else hist["Open"].iloc[-1]
            pct = (price - prev) / prev * 100
            info = get_info(t)
            rows.append({
                "Ticker":  t,
                "Last":    f"{price:,.2f}",
                "Chg%":    f"{pct:+.2f}%",
                "Mkt Cap": fmt_big(info.get("marketCap")),
                "P/E":     fmt_num(info.get("trailingPE")),
            })

        df = pd.DataFrame(rows)
        styled = (
            df.style
            .set_properties(**{
                "background-color": "#ffffff",
                "color": "#111827",
                "font-family": "JetBrains Mono, monospace",
                "font-size": "13px",
            })
            .map(color_signed, subset=["Chg%"])
        )
        st.dataframe(styled, width="stretch", hide_index=True)

    with col2:
        pick_col, custom_col = st.columns([1, 1])
        with pick_col:
            selected_ticker = st.selectbox("Sector Ticker", tickers, key="chart_ticker")
        with custom_col:
            custom_ticker = st.text_input(
                "Or any ticker",
                placeholder="e.g. NVDA, AAPL, TSLA, ^GSPC",
                key="custom_ticker",
            ).strip().upper()

        chart_ticker = custom_ticker if custom_ticker else selected_ticker

        # Fetch history first so we can compute period return for the header
        hist = get_history(chart_ticker, period=period)

        # Header row: ticker info on the left, period return on the right
        h_left, h_right = st.columns([3, 1])
        with h_left:
            price_line_html = ""
            if not hist.empty:
                current = float(hist["Close"].iloc[-1])
                prefix = "" if chart_ticker.startswith("^") else "$"
                price_line_html = (
                    f'<div style="font-family:\'JetBrains Mono\',monospace; '
                    f'font-size:28px; font-weight:700; color:#111827; '
                    f'letter-spacing:-0.02em; margin-top:6px;">'
                    f'{prefix}{current:,.2f}</div>'
                )
            st.markdown(
                f'<div class="kicker">{period.upper()} · {chart_type}</div>'
                f'<div class="panel-title">{chart_ticker}</div>'
                f'{price_line_html}',
                unsafe_allow_html=True,
            )
        with h_right:
            if not hist.empty and len(hist) >= 2:
                start_px = float(hist["Close"].iloc[0])
                end_px = float(hist["Close"].iloc[-1])
                ret_pct = (end_px - start_px) / start_px * 100
                ret_abs = end_px - start_px
                sign = "+" if ret_pct >= 0 else ""
                color = "#059669" if ret_pct >= 0 else "#dc2626"
                st.markdown(
                    f'<div style="text-align:right; padding-top:10px;">'
                    f'<div style="font-family:Inter,sans-serif; font-size:10px; '
                    f'color:#6b7280; text-transform:uppercase; letter-spacing:0.1em; '
                    f'margin-bottom:2px;">{period.upper()} Return</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace; '
                    f'font-size:22px; font-weight:600; color:{color};">'
                    f'{sign}{ret_pct:.2f}%</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace; '
                    f'font-size:11px; color:#6b7280;">'
                    f'{sign}${ret_abs:,.2f} per share</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        if hist.empty:
            st.warning(f"No data found for '{chart_ticker}'. Check the symbol and try again.")
        else:
            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True,
                vertical_spacing=0.03, row_heights=[0.75, 0.25],
            )

            if chart_type == "Candlestick":
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist["Open"], high=hist["High"],
                    low=hist["Low"], close=hist["Close"],
                    increasing_line_color="#059669",
                    decreasing_line_color="#dc2626",
                ), row=1, col=1)
            elif chart_type == "Area":
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist["Close"],
                    mode="lines", fill="tozeroy",
                    line=dict(color="#2563eb", width=2),
                    fillcolor="rgba(37,99,235,0.12)",
                ), row=1, col=1)
                fig.update_yaxes(
                    range=[hist["Close"].min() * 0.95, hist["Close"].max() * 1.05],
                    row=1, col=1,
                )
            else:
                fig.add_trace(go.Scatter(
                    x=hist.index, y=hist["Close"],
                    mode="lines",
                    line=dict(color="#2563eb", width=2),
                ), row=1, col=1)

            vol_colors = [
                "#059669" if c >= o else "#dc2626"
                for o, c in zip(hist["Open"], hist["Close"])
            ]
            fig.add_trace(go.Bar(
                x=hist.index, y=hist["Volume"],
                marker_color=vol_colors, showlegend=False,
            ), row=2, col=1)

            fig.update_layout(
                template="simple_white",
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
                height=500,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_rangeslider_visible=False,
                showlegend=False,
                font=dict(family="Inter, sans-serif", color="#111827", size=11),
            )
            fig.update_xaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                             linecolor="#e5e7eb", showline=True)
            fig.update_yaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                             linecolor="#e5e7eb", showline=True)

            st.plotly_chart(fig, width="stretch")

    # ---- Fundamentals ----
    st.markdown(
        f'<div class="kicker">Company Fundamentals</div>'
        f'<div class="panel-title">{chart_ticker}</div>',
        unsafe_allow_html=True,
    )
    info = get_info(chart_ticker)

    r1 = st.columns(4)
    r1[0].metric("P/E (TTM)",    fmt_num(info.get("trailingPE")))
    r1[1].metric("Forward P/E",  fmt_num(info.get("forwardPE")))
    r1[2].metric("Price / Book", fmt_num(info.get("priceToBook")))
    r1[3].metric("Beta",         fmt_num(info.get("beta")))

    r2 = st.columns(4)
    r2[0].metric("Market Cap",    fmt_big(info.get("marketCap")))
    r2[1].metric("Revenue (TTM)", fmt_big(info.get("totalRevenue")))
    r2[2].metric("EBITDA",        fmt_big(info.get("ebitda")))
    r2[3].metric("Net Income",    fmt_big(info.get("netIncomeToCommon")))

    r3 = st.columns(4)
    r3[0].metric("ROE",            fmt_pct(info.get("returnOnEquity")))
    r3[1].metric("ROA",            fmt_pct(info.get("returnOnAssets")))
    r3[2].metric("Profit Margin",  fmt_pct(info.get("profitMargins")))
    r3[3].metric("Dividend Yield", fmt_pct(info.get("dividendYield")))

    r4 = st.columns(4)
    r4[0].metric("52W High",   fmt_num(info.get("fiftyTwoWeekHigh")))
    r4[1].metric("52W Low",    fmt_num(info.get("fiftyTwoWeekLow")))
    r4[2].metric("Avg Volume", fmt_big(info.get("averageVolume")))
    r4[3].metric("Shares Out", fmt_big(info.get("sharesOutstanding")))

    desc = info.get("longBusinessSummary")
    if desc:
        with st.expander(f"About {info.get('longName', chart_ticker)}"):
            st.write(desc)

    # ---- Macro News ----
    st.markdown('<div class="panel-title">Macro Headlines</div>', unsafe_allow_html=True)
    news = fetch_macro_news(limit=10)
    if not news:
        st.info("No news available right now.")
    else:
        news_html = []
        for item in news:
            when = format_news_time(item.get("pub_time"))
            link = item.get("url") or "#"
            news_html.append(f"""
                <div class="news-item">
                    <a href="{link}" target="_blank" class="headline">{item["title"]}</a>
                    <div class="meta">
                        <span class="publisher">{item["publisher"]}</span>
                        {'· ' + when if when else ''}
                    </div>
                </div>
            """)
        st.markdown("".join(news_html), unsafe_allow_html=True)

# =========================================================================
# PORTFOLIO TAB
# =========================================================================
with tab_portfolio:
    # ---- Holdings table + summary ----
    st.markdown('<div class="panel-title">Holdings</div>', unsafe_allow_html=True)

    holdings_rows = []
    for h in FUND_HOLDINGS:
        hist = get_history(h["ticker"], period="5d")
        info = get_info(h["ticker"])
        if hist.empty:
            continue
        price = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(hist["Open"].iloc[-1])
        day_pct = (price - prev) / prev * 100
        mv = price * h["shares"]
        cost = h["cost_basis"] * h["shares"]
        unreal = mv - cost
        unreal_pct = (price / h["cost_basis"] - 1) * 100

        holdings_rows.append({
            "Ticker":       h["ticker"],
            "Name":         info.get("shortName", h["ticker"]),
            "Shares":       f"{h['shares']:,}",
            "Last":         f"{price:,.2f}",
            "Day %":        f"{day_pct:+.2f}%",
            "Cost Basis":   f"{h['cost_basis']:,.2f}",
            "Market Value": f"${mv:,.0f}",
            "Unreal P&L":   f"${unreal:+,.0f}",
            "Unreal %":     f"{unreal_pct:+.2f}%",
            "_mv":          mv,
        })

    total_mv = sum(r["_mv"] for r in holdings_rows)
    for row in holdings_rows:
        row["Weight"] = f"{(row['_mv'] / total_mv * 100):.2f}%" if total_mv else "—"

    if holdings_rows:
        holdings_df = pd.DataFrame(holdings_rows)[[
            "Ticker", "Name", "Shares", "Last", "Day %",
            "Cost Basis", "Market Value", "Unreal P&L", "Unreal %", "Weight",
        ]]

        holdings_styled = (
            holdings_df.style
            .set_properties(**{
                "background-color": "#ffffff",
                "color": "#111827",
                "font-family": "JetBrains Mono, monospace",
                "font-size": "13px",
            })
            .map(color_signed, subset=["Day %", "Unreal P&L", "Unreal %"])
        )

        c_hold, c_summary = st.columns([4, 1])
        with c_hold:
            st.dataframe(holdings_styled, width="stretch", hide_index=True)
        with c_summary:
            total_cost = sum(h["shares"] * h["cost_basis"] for h in FUND_HOLDINGS)
            total_pnl = total_mv - total_cost
            st.metric("Market Value", f"${total_mv:,.0f}")
            st.metric(
                "Unrealized P&L",
                f"${total_pnl:+,.0f}",
                delta=f"{(total_pnl/total_cost*100):+.2f}%" if total_cost else None,
            )
    else:
        st.info("No holdings to display. Add trades to FUND_TRADES in the source file.")

    # ---- Performance chart ----
    st.markdown(
        '<div class="kicker">Since Inception</div>'
        '<div class="panel-title">Portfolio Performance</div>',
        unsafe_allow_html=True,
    )
    perf_df = compute_portfolio_history(FUND_TRADES)
    if perf_df.empty or len(perf_df) < 2:
        st.info(
            "Not enough trading history yet to plot a performance curve. "
            "Chart will populate once your holdings have at least two trading days of data."
        )
    else:
        perf_fig = go.Figure()
        # Cost basis reference (flat-ish line stepping up with each buy)
        perf_fig.add_trace(go.Scatter(
            x=perf_df["Date"], y=perf_df["Cost"],
            mode="lines",
            line=dict(color="#9ca3af", width=1.5, dash="dot"),
            name="Cost Basis",
        ))
        # Market value
        perf_fig.add_trace(go.Scatter(
            x=perf_df["Date"], y=perf_df["Value"],
            mode="lines", fill="tonexty",
            line=dict(color="#2563eb", width=2.2),
            fillcolor="rgba(37,99,235,0.10)",
            name="Market Value",
        ))
        perf_fig.update_layout(
            template="simple_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
            ),
            font=dict(family="Inter, sans-serif", color="#111827", size=11),
            hovermode="x unified",
        )
        perf_fig.update_xaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                              linecolor="#e5e7eb", showline=True)
        perf_fig.update_yaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                              linecolor="#e5e7eb", showline=True,
                              tickformat="$,.0f")
        st.plotly_chart(perf_fig, width="stretch")

    # ---- Trade blotter ----
    st.markdown('<div class="panel-title">Trade Blotter</div>', unsafe_allow_html=True)
    trades_df = pd.DataFrame(FUND_TRADES)
    if not trades_df.empty:
        trades_df = trades_df.sort_values("date", ascending=False)
        trades_df["price"] = trades_df["price"].map(lambda x: f"${x:,.2f}")
        trades_df["shares"] = trades_df["shares"].map(lambda x: f"{x:,}")
        trades_df.columns = [c.capitalize() for c in trades_df.columns]
        trades_styled = trades_df.style.set_properties(**{
            "background-color": "#ffffff",
            "color": "#111827",
            "font-family": "JetBrains Mono, monospace",
            "font-size": "13px",
        })
        st.dataframe(trades_styled, width="stretch", hide_index=True)
    else:
        st.info("No trades logged yet.")


# =========================================================================
# INDUSTRIES TAB
# =========================================================================
with tab_industries:
    # ---- Sectors ----
    st.markdown(
        '<div class="kicker">S&P 500 via SPDR Select Sector ETFs</div>'
        '<div class="panel-title">Sector Performance</div>',
        unsafe_allow_html=True,
    )

    sort_col_sec = st.selectbox(
        "Sort by",
        ["1D", "1W", "1M", "3M", "YTD", "1Y"],
        index=0,
        key="sector_sort",
    )

    sector_perf = build_performance_table(SECTOR_ETFS)
    if not sector_perf.empty:
        sector_sorted = sector_perf.sort_values(
            sort_col_sec, ascending=False, na_position="last"
        )
        st.dataframe(format_and_style_perf(sector_sorted), width="stretch", hide_index=True)
    else:
        st.warning("Could not load sector data. Try refreshing in a minute.")

    # ---- Industries ----
    st.markdown(
        '<div class="kicker">Sub-Industry and Macro Proxies</div>'
        '<div class="panel-title">Industry Groups</div>',
        unsafe_allow_html=True,
    )

    sort_col_ind = st.selectbox(
        "Sort by",
        ["1D", "1W", "1M", "3M", "YTD", "1Y"],
        index=0,
        key="industry_sort",
    )

    industry_perf = build_performance_table(INDUSTRY_ETFS)
    if not industry_perf.empty:
        industry_sorted = industry_perf.sort_values(
            sort_col_ind, ascending=False, na_position="last"
        )
        st.dataframe(format_and_style_perf(industry_sorted), width="stretch", hide_index=True)
    else:
        st.warning("Could not load industry data. Try refreshing in a minute.")

    # ---- Relative Performance Chart ----
    st.markdown(
        '<div class="kicker">Normalized to 100 at Start</div>'
        '<div class="panel-title">Relative Performance</div>',
        unsafe_allow_html=True,
    )

    all_groups = {**SECTOR_ETFS, **INDUSTRY_ETFS}
    all_names = list(all_groups.keys())
    default_selection = [n for n in ["Technology", "Financials", "Energy", "Health Care"]
                         if n in all_names]

    ctrl_left, ctrl_right = st.columns([3, 1])
    with ctrl_left:
        selected = st.multiselect(
            "Select groups to compare",
            all_names,
            default=default_selection,
            key="rel_perf_select",
        )
    with ctrl_right:
        rel_period = st.select_slider(
            "Lookback",
            options=["1mo", "3mo", "6mo", "1y"],
            value="3mo",
            key="rel_perf_period",
        )

    if not selected:
        st.info("Pick at least one group above to see relative performance.")
    else:
        # Distinct colors — extended if lots selected
        palette = ["#2563eb", "#059669", "#dc2626", "#d97706",
                   "#7c3aed", "#db2777", "#0891b2", "#ca8a04",
                   "#4338ca", "#047857", "#b91c1c", "#a16207"]
        rel_fig = go.Figure()

        for i, name in enumerate(selected):
            ticker = all_groups[name]
            rel_hist = get_history(ticker, period=rel_period)
            if rel_hist.empty or len(rel_hist) < 2:
                continue
            closes = rel_hist["Close"]
            normalized = closes / float(closes.iloc[0]) * 100
            rel_fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized.values,
                mode="lines",
                name=name,
                line=dict(color=palette[i % len(palette)], width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%b %d, %Y}}<br>%{{y:.2f}}<extra></extra>",
            ))

        # Reference line at 100
        rel_fig.add_hline(
            y=100, line_dash="dash", line_color="#9ca3af", line_width=1,
            annotation_text="Start", annotation_position="right",
            annotation_font=dict(family="Inter, sans-serif", size=10, color="#9ca3af"),
        )

        rel_fig.update_layout(
            template="simple_white",
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            height=420,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
                font=dict(family="Inter, sans-serif", size=11, color="#6b7280"),
            ),
            font=dict(family="Inter, sans-serif", color="#111827", size=11),
            hovermode="x unified",
        )
        rel_fig.update_xaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                             linecolor="#e5e7eb", showline=True)
        rel_fig.update_yaxes(gridcolor="#f3f4f6", zerolinecolor="#e5e7eb",
                             linecolor="#e5e7eb", showline=True,
                             tickformat=".1f")

        st.plotly_chart(rel_fig, width="stretch")
