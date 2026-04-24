import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

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


@st.cache_data(ttl=3600, show_spinner=False)
def get_info(ticker):
    try:
        return yf.Ticker(ticker, session=get_session()).info or {}
    except Exception:
        return {}


def color_signed(val):
    """Green for positive, red for negative. Handles strings, numbers, and NaN."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    try:
        v = float(
            str(val).replace("%", "").replace("+", "")
            .replace("$", "").replace(",", "")
        )
        if pd.isna(v):
            return ""
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
    """Style a performance DataFrame. Keeps underlying values numeric so that
    clicking a column header in st.dataframe sorts correctly (pandas/Streamlit
    sort on the raw values, not the formatted display strings)."""
    d = df.rename(columns={
        "1D": "1D %", "1W": "1W %", "1M": "1M %",
        "3M": "3M %", "YTD": "YTD %", "1Y": "1Y %",
    })
    pct_cols = ["1D %", "1W %", "1M %", "3M %", "YTD %", "1Y %"]

    def _pct_fmt(v):
        return f"{v:+.2f}%" if pd.notna(v) else "—"

    def _last_fmt(v):
        return f"{v:,.2f}" if pd.notna(v) else "—"

    formatter = {col: _pct_fmt for col in pct_cols}
    formatter["Last"] = _last_fmt

    return (
        d.style
        .format(formatter)
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
# CHART PERIODS
# =========================
PERIOD_OPTIONS = ["1D", "5D", "1M", "6M", "YTD", "1Y", "3Y", "5Y", "All"]


@st.cache_data(ttl=300, show_spinner=False)
def get_chart_history(ticker, period_label):
    """Fetch chart history for a user-friendly period label.

    1D / 5D use intraday intervals; everything else is daily bars.
    YTD computes from Jan 1 of current year; All uses yfinance's full history.
    """
    try:
        tk = yf.Ticker(ticker, session=get_session())
        if period_label == "1D":
            return tk.history(period="1d", interval="5m")
        if period_label == "5D":
            return tk.history(period="5d", interval="30m")
        if period_label == "YTD":
            start = f"{datetime.now().year}-01-01"
            return tk.history(start=start, interval="1d")
        if period_label == "All":
            return tk.history(period="max", interval="1d")
        mapping = {"1M": "1mo", "6M": "6mo", "1Y": "1y", "3Y": "3y", "5Y": "5y"}
        return tk.history(period=mapping.get(period_label, "6mo"), interval="1d")
    except Exception:
        return pd.DataFrame()


# =========================
# ECONOMIC CALENDAR
# =========================
# Known high-impact events. FOMC meeting dates come from the Federal Reserve's
# published annual schedule. CPI / PPI / GDP / Retail Sales dates are the BLS
# and BEA's typical release patterns and should be verified day-of via the
# official sources before trading decisions.
STATIC_ECONOMIC_EVENTS = [
    # FOMC 2026 — from Federal Reserve publication
    {"date": "2026-04-29", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    {"date": "2026-06-17", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    {"date": "2026-07-29", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    {"date": "2026-09-16", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    {"date": "2026-10-28", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    {"date": "2026-12-09", "event": "FOMC Rate Decision",     "category": "Fed",       "importance": "High"},
    # CPI — typically second Tuesday of the month
    {"date": "2026-05-12", "event": "CPI (April)",            "category": "Inflation", "importance": "High"},
    {"date": "2026-06-11", "event": "CPI (May)",              "category": "Inflation", "importance": "High"},
    {"date": "2026-07-14", "event": "CPI (June)",             "category": "Inflation", "importance": "High"},
    {"date": "2026-08-12", "event": "CPI (July)",             "category": "Inflation", "importance": "High"},
    {"date": "2026-09-10", "event": "CPI (August)",           "category": "Inflation", "importance": "High"},
    {"date": "2026-10-13", "event": "CPI (September)",        "category": "Inflation", "importance": "High"},
    {"date": "2026-11-12", "event": "CPI (October)",          "category": "Inflation", "importance": "High"},
    {"date": "2026-12-10", "event": "CPI (November)",         "category": "Inflation", "importance": "High"},
    # PPI — usually day after CPI
    {"date": "2026-05-13", "event": "PPI (April)",            "category": "Inflation", "importance": "Medium"},
    {"date": "2026-06-12", "event": "PPI (May)",              "category": "Inflation", "importance": "Medium"},
    {"date": "2026-07-15", "event": "PPI (June)",             "category": "Inflation", "importance": "Medium"},
    {"date": "2026-08-13", "event": "PPI (July)",             "category": "Inflation", "importance": "Medium"},
    # GDP (quarterly)
    {"date": "2026-04-30", "event": "GDP Q1 (Advance)",       "category": "Growth",    "importance": "High"},
    {"date": "2026-05-29", "event": "GDP Q1 (2nd Estimate)",  "category": "Growth",    "importance": "Medium"},
    {"date": "2026-06-26", "event": "GDP Q1 (3rd Estimate)",  "category": "Growth",    "importance": "Low"},
    {"date": "2026-07-30", "event": "GDP Q2 (Advance)",       "category": "Growth",    "importance": "High"},
    {"date": "2026-08-28", "event": "GDP Q2 (2nd Estimate)",  "category": "Growth",    "importance": "Medium"},
    {"date": "2026-10-30", "event": "GDP Q3 (Advance)",       "category": "Growth",    "importance": "High"},
    # Retail Sales (mid-month)
    {"date": "2026-05-15", "event": "Retail Sales (April)",   "category": "Consumer",  "importance": "Medium"},
    {"date": "2026-06-17", "event": "Retail Sales (May)",     "category": "Consumer",  "importance": "Medium"},
    {"date": "2026-07-16", "event": "Retail Sales (June)",    "category": "Consumer",  "importance": "Medium"},
    {"date": "2026-08-17", "event": "Retail Sales (July)",    "category": "Consumer",  "importance": "Medium"},
    # Earnings season kickoffs (rough)
    {"date": "2026-07-14", "event": "Q2 Earnings Season Begins", "category": "Earnings", "importance": "Medium"},
    {"date": "2026-10-13", "event": "Q3 Earnings Season Begins", "category": "Earnings", "importance": "Medium"},
]


def _first_friday(year, month):
    """First Friday of a given month — used for NFP release dates."""
    first = datetime(year, month, 1)
    offset = (4 - first.weekday()) % 7  # Friday is weekday index 4
    return (first + timedelta(days=offset)).date()


def get_upcoming_events(days_ahead=60):
    """Compile upcoming events: static list + dynamically-computed NFP dates.

    NFP is always the first Friday of the month, so we compute it rather than
    hard-code. Other monthly economic data releases (CPI/PPI/Retail Sales) use
    the typical pattern but actual dates are set by BLS each month.
    """
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    events = []

    # Static events within the window
    for e in STATIC_ECONOMIC_EVENTS:
        try:
            dt = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        if today <= dt <= cutoff:
            events.append({**e, "_date": dt})

    # Dynamically compute NFP (first Friday of each month in window)
    current = today.replace(day=1)
    while current <= cutoff:
        nfp = _first_friday(current.year, current.month)
        if today <= nfp <= cutoff:
            prev_month_date = current - timedelta(days=1)
            prev_month_name = prev_month_date.strftime("%B") if prev_month_date.month != current.month else current.strftime("%B")
            events.append({
                "date": nfp.strftime("%Y-%m-%d"),
                "event": f"Nonfarm Payrolls ({prev_month_name})",
                "category": "Jobs",
                "importance": "High",
                "_date": nfp,
            })
        # Advance to next month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)

    # Dedupe by (date, event) just in case
    seen, unique = set(), []
    for e in events:
        key = (e["_date"], e["event"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    unique.sort(key=lambda x: x["_date"])
    return unique


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
# SIDEBAR — Watchlist
# =========================
# Subsectors dict is used by the Financials tab
subsectors = {
    "Banks":          ["JPM", "BAC", "WFC", "C", "GS", "MS"],
    "Asset Managers": ["BLK", "TROW", "KKR", "APO", "BX"],
    "Insurance":      ["AIG", "ALL", "MET", "PRU", "TRV"],
    "Payments":       ["V", "MA", "PYPL", "AXP", "COF"],
}

# Initialize watchlist — reads from URL query params if present (so bookmarking
# the URL preserves the watchlist across sessions / devices), otherwise uses
# sensible defaults.
DEFAULT_WATCHLIST = ["^GSPC", "AAPL", "MSFT", "NVDA", "META", "TSLA"]


def _watchlist_from_query():
    try:
        qp_val = st.query_params.get("wl", "")
    except Exception:
        qp_val = ""
    if not qp_val:
        return None
    parts = [t.strip().upper() for t in qp_val.split(",") if t.strip()]
    # Dedupe while preserving order
    seen, unique = set(), []
    for t in parts:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return unique or None


def _sync_watchlist_to_query():
    """Write the current watchlist to the URL so refreshes/bookmarks keep it."""
    try:
        if st.session_state.watchlist:
            st.query_params["wl"] = ",".join(st.session_state.watchlist)
        else:
            # Clear the param rather than leaving an empty value
            if "wl" in st.query_params:
                del st.query_params["wl"]
    except Exception:
        pass  # older Streamlit — fail silently, session_state still works


if "watchlist" not in st.session_state:
    st.session_state.watchlist = _watchlist_from_query() or list(DEFAULT_WATCHLIST)

st.sidebar.markdown('<div class="panel-title">Watchlist</div>', unsafe_allow_html=True)

# Add-ticker form (clears input on submit)
with st.sidebar.form("add_watchlist_form", clear_on_submit=True):
    new_ticker = st.text_input(
        "Add",
        placeholder="Add ticker (e.g. TSLA)",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Add to Watchlist", use_container_width=True)
    if submitted and new_ticker:
        new_clean = new_ticker.strip().upper()
        if new_clean and new_clean not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_clean)
            _sync_watchlist_to_query()
            st.rerun()

# Render each watchlist row with inline remove button
for t in list(st.session_state.watchlist):
    c_left, c_right = st.sidebar.columns([5, 1], gap="small", vertical_alignment="center")
    with c_left:
        hist = get_history(t, period="5d")
        if not hist.empty and len(hist) >= 2:
            price = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2])
            pct = (price - prev) / prev * 100
            pct_color = "#059669" if pct >= 0 else "#dc2626"
            prefix = "" if t.startswith("^") else "$"
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace; '
                f'font-size:12px; padding:6px 0; border-bottom:1px solid #f3f4f6;">'
                f'<div style="display:flex; justify-content:space-between; align-items:baseline;">'
                f'<span style="font-weight:600; color:#111827;">{t}</span>'
                f'<span style="color:{pct_color}; font-weight:500;">{pct:+.2f}%</span>'
                f'</div>'
                f'<div style="color:#6b7280; font-size:11px; margin-top:2px;">{prefix}{price:,.2f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace; '
                f'font-size:12px; padding:6px 0; color:#9ca3af; '
                f'border-bottom:1px solid #f3f4f6;">{t} — no data</div>',
                unsafe_allow_html=True,
            )
    with c_right:
        if st.button("×", key=f"wl_rm_{t}", help=f"Remove {t}"):
            st.session_state.watchlist.remove(t)
            _sync_watchlist_to_query()
            st.rerun()

# =========================
# TABS
# =========================
tab_markets, tab_industries, tab_calendar, tab_financials = st.tabs(
    ["Markets", "Industries", "Calendar", "Financials"]
)

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

    # ---- Chart (full-width) ----
    chart_ticker = st.text_input(
        "Ticker",
        value="^GSPC",
        placeholder="e.g. AAPL, NVDA, ^GSPC, BTC-USD",
        help="Any ticker yfinance supports. Indices use ^ prefix (^GSPC, ^IXIC, ^VIX). "
             "Crypto uses -USD suffix (BTC-USD, ETH-USD). International tickers use "
             "exchange suffixes (HSBA.L for London, 7203.T for Tokyo).",
        key="chart_ticker_input",
    ).strip().upper() or "^GSPC"

    # Period selector (segmented control) + chart type (selectbox) side by side
    period_col, type_col = st.columns([3, 1])
    with period_col:
        period_label = st.segmented_control(
            "Period",
            options=PERIOD_OPTIONS,
            default="6M",
            label_visibility="collapsed",
            key="chart_period_sc",
        )
        if not period_label:
            period_label = "6M"
    with type_col:
        chart_type = st.selectbox(
            "Chart Type",
            ["Candlestick", "Line", "Area"],
            index=0,
            label_visibility="collapsed",
            key="chart_type_select",
        )

    # Fetch history for the selected period
    hist = get_chart_history(chart_ticker, period_label)

    # Header row: ticker info on the left, period return on the right
    h_left, h_right = st.columns([3, 1])
    with h_left:
        price_line_html = ""
        if not hist.empty:
            current = float(hist["Close"].iloc[-1])
            prefix = "" if chart_ticker.startswith("^") else "$"
            price_line_html = (
                f'<div style="font-family:\'JetBrains Mono\',monospace; '
                f'font-size:32px; font-weight:700; color:#111827; '
                f'letter-spacing:-0.02em; margin-top:6px;">'
                f'{prefix}{current:,.2f}</div>'
            )
        st.markdown(
            f'<div class="kicker">{period_label} · {chart_type}</div>'
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
                f'margin-bottom:2px;">{period_label} Return</div>'
                f'<div style="font-family:\'JetBrains Mono\',monospace; '
                f'font-size:24px; font-weight:600; color:{color};">'
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
            height=620,
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

    # Earnings yield = 1 / P/E (decimal form, fmt_pct will show as percentage)
    te_pe = info.get("trailingPE")
    earnings_yield = (1 / te_pe) if te_pe and te_pe != 0 else None

    r1 = st.columns(4)
    r1[0].metric("P/E (TTM)",      fmt_num(info.get("trailingPE")))
    r1[1].metric("Forward P/E",    fmt_num(info.get("forwardPE")))
    r1[2].metric("EPS (TTM)",      fmt_num(info.get("trailingEps")))
    r1[3].metric("Earnings Yield", fmt_pct(earnings_yield))

    r2 = st.columns(4)
    r2[0].metric("Price / Book",   fmt_num(info.get("priceToBook")))
    r2[1].metric("Beta",           fmt_num(info.get("beta")))
    r2[2].metric("Market Cap",     fmt_big(info.get("marketCap")))
    r2[3].metric("Dividend Yield", fmt_pct(info.get("dividendYield")))

    r3 = st.columns(4)
    r3[0].metric("Gross Margin",     fmt_pct(info.get("grossMargins")))
    r3[1].metric("Operating Margin", fmt_pct(info.get("operatingMargins")))
    r3[2].metric("EBITDA Margin",    fmt_pct(info.get("ebitdaMargins")))
    r3[3].metric("Profit Margin",    fmt_pct(info.get("profitMargins")))

    r4 = st.columns(4)
    r4[0].metric("ROE",       fmt_pct(info.get("returnOnEquity")))
    r4[1].metric("ROA",       fmt_pct(info.get("returnOnAssets")))
    r4[2].metric("52W High",  fmt_num(info.get("fiftyTwoWeekHigh")))
    r4[3].metric("52W Low",   fmt_num(info.get("fiftyTwoWeekLow")))

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
# FINANCIALS TAB
# =========================================================================
def _build_subsector_table(ticker_list):
    """Build a quote DataFrame for a list of tickers."""
    rows = []
    for t in ticker_list:
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
    return pd.DataFrame(rows)


def _render_subsector(name, ticker_list):
    """Render one subsector block: header, quote table."""
    st.markdown(
        f'<div class="kicker">{len(ticker_list)} names</div>'
        f'<div class="panel-title">{name}</div>',
        unsafe_allow_html=True,
    )
    df = _build_subsector_table(ticker_list)
    if df.empty:
        st.warning(f"Could not load {name} data.")
        return
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


with tab_financials:
    st.markdown(
        '<div class="kicker">Large-Cap U.S. Financials</div>'
        '<div class="panel-title">Sector Overview</div>',
        unsafe_allow_html=True,
    )

    # 2x2 grid of subsectors
    row1_left, row1_right = st.columns(2)
    with row1_left:
        _render_subsector("Banks", subsectors["Banks"])
    with row1_right:
        _render_subsector("Insurance", subsectors["Insurance"])

    row2_left, row2_right = st.columns(2)
    with row2_left:
        _render_subsector("Asset Managers", subsectors["Asset Managers"])
    with row2_right:
        _render_subsector("Payments", subsectors["Payments"])


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

    selected = st.multiselect(
        "Select groups to compare",
        all_names,
        default=default_selection,
        key="rel_perf_select",
    )

    rel_period = st.segmented_control(
        "Lookback",
        options=PERIOD_OPTIONS,
        default="3M",
        label_visibility="collapsed",
        key="rel_perf_period_sc",
    )
    if not rel_period:
        rel_period = "3M"

    if not selected:
        st.info("Pick at least one group above to see relative performance.")
    else:
        palette = ["#2563eb", "#059669", "#dc2626", "#d97706",
                   "#7c3aed", "#db2777", "#0891b2", "#ca8a04",
                   "#4338ca", "#047857", "#b91c1c", "#a16207"]
        rel_fig = go.Figure()

        for i, name in enumerate(selected):
            ticker = all_groups[name]
            rel_hist = get_chart_history(ticker, rel_period)
            if rel_hist.empty or len(rel_hist) < 2:
                continue
            closes = rel_hist["Close"]
            start_px = float(closes.iloc[0])
            end_px = float(closes.iloc[-1])
            ret_pct = (end_px - start_px) / start_px * 100
            normalized = closes / start_px * 100

            sign = "+" if ret_pct >= 0 else ""
            legend_name = f"{name}  {sign}{ret_pct:.2f}%"

            rel_fig.add_trace(go.Scatter(
                x=normalized.index,
                y=normalized.values,
                mode="lines",
                name=legend_name,
                line=dict(color=palette[i % len(palette)], width=2),
                hovertemplate=f"<b>{name}</b><br>%{{x|%b %d, %Y}}<br>%{{y:.2f}}<extra></extra>",
            ))

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
                font=dict(family="JetBrains Mono, monospace", size=12, color="#111827"),
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


# =========================================================================
# CALENDAR TAB
# =========================================================================
with tab_calendar:
    st.markdown(
        '<div class="kicker">Key Macro Events Ahead</div>'
        '<div class="panel-title">Economic Calendar</div>',
        unsafe_allow_html=True,
    )

    # Lookahead selector
    days_ahead = st.segmented_control(
        "Lookahead",
        options=[14, 30, 60, 90],
        format_func=lambda d: f"{d} days",
        default=30,
        label_visibility="collapsed",
        key="cal_lookahead",
    )
    if not days_ahead:
        days_ahead = 30

    events = get_upcoming_events(days_ahead=days_ahead)

    if not events:
        st.info(f"No upcoming events in the next {days_ahead} days.")
    else:
        today_d = datetime.now().date()
        rows = []
        for e in events:
            delta = (e["_date"] - today_d).days
            if delta == 0:
                when = "Today"
            elif delta == 1:
                when = "Tomorrow"
            elif delta < 7:
                when = f"In {delta} days"
            elif delta < 14:
                when = f"Next week"
            else:
                when = f"In {delta} days"

            rows.append({
                "Date":       e["_date"].strftime("%a, %b %d"),
                "Event":      e["event"],
                "Category":   e["category"],
                "Importance": e["importance"],
                "When":       when,
            })

        df = pd.DataFrame(rows)

        def _importance_color(val):
            if val == "High":
                return "color: #dc2626; font-weight: 600;"
            if val == "Medium":
                return "color: #d97706; font-weight: 500;"
            return "color: #6b7280;"

        styled = (
            df.style
            .set_properties(**{
                "background-color": "#ffffff",
                "color": "#111827",
                "font-family": "Inter, sans-serif",
                "font-size": "13px",
            })
            .map(_importance_color, subset=["Importance"])
        )
        st.dataframe(styled, width="stretch", hide_index=True)

    # Methodology / disclaimer
    st.markdown(
        '<div style="margin-top:20px; padding:14px 18px; background:#f9fafb; '
        'border-left:3px solid #6b7280; font-family:Inter,sans-serif; '
        'font-size:12px; color:#6b7280; line-height:1.6;">'
        '<strong style="color:#111827;">Methodology.</strong> FOMC meeting dates come from '
        'the Federal Reserve\'s published schedule. Nonfarm Payrolls are computed as the '
        'first Friday of each month (BLS standard). CPI, PPI, GDP, and Retail Sales dates '
        'follow typical monthly patterns but specific release dates are set by the BLS / BEA '
        'each month — cross-reference with official sources for day-of trading decisions.'
        '</div>',
        unsafe_allow_html=True,
    )
