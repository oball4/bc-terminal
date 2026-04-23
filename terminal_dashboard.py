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
    page_title="BC Terminal",
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
# STYLE — LIGHT MODE / NAVY ACCENT
# =========================
# Palette:
#   background  #ffffff   white
#   panel       #f9fafb   subtle off-white
#   border      #e5e7eb   light grey
#   text        #111827   near-black
#   muted       #6b7280   grey
#   deep navy   #0a1938   banner background
#   accent blue #2563eb   highlights / kickers
#   gain        #059669   green (darker for contrast)
#   loss        #dc2626   red   (darker for contrast)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

.stApp {
    background-color: #ffffff;
    color: #111827;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Scoped text overrides — do NOT touch universal span/div (would break icons) */
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

/* Sidebar — subtle off-white */
[data-testid="stSidebar"] {
    background-color: #f9fafb;
    border-right: 1px solid #e5e7eb;
}

/* Metric cards */
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

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}

/* Text inputs */
[data-testid="stTextInput"] input {
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1px solid #e5e7eb !important;
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* Top banner — navy keeps its presence on white */
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

/* Hide only the three-dot menu and footer. KEEP the header element visible
   so the sidebar expand button ("»") still renders when the sidebar is
   collapsed — hiding the whole header removes that button. */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] {
    background-color: transparent;
}
[data-testid="collapsedControl"] {
    visibility: visible !important;
    display: block !important;
    z-index: 999999 !important;
}

hr {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 16px 0;
}
</style>
""", unsafe_allow_html=True)


# =========================
# OPTIONAL PASSWORD GATE
# =========================
# If a "password" entry exists in Streamlit secrets, lock the app behind it.
# Locally (no secrets configured) the gate is inert, so development is easy.
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
        st.markdown("### BC Terminal")
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


@st.cache_data(ttl=60, show_spinner=False)
def get_history(ticker, period="1d", interval="1d"):
    return yf.Ticker(ticker).history(period=period, interval=interval)


@st.cache_data(ttl=300, show_spinner=False)
def get_info(ticker):
    try:
        return yf.Ticker(ticker).info or {}
    except Exception:
        return {}


def color_signed(val):
    """Green for positive, red for negative."""
    try:
        v = float(
            str(val).replace("%", "").replace("+", "")
            .replace("$", "").replace(",", "")
        )
        return "color: #059669" if v >= 0 else "color: #dc2626"
    except Exception:
        return ""


# =========================
# TOP BANNER
# =========================
today = datetime.now()
st.markdown(
    f"""
    <div class="banner">
        <div class="title">
            <span class="mark">■</span>
            <span>BC Terminal</span>
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
# GLOBAL INDICES
# =========================
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

# =========================
# FUND HOLDINGS
# =========================
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

holdings_df = pd.DataFrame(holdings_rows)[[
    "Ticker", "Name", "Shares", "Last", "Day %",
    "Cost Basis", "Market Value", "Unreal P&L", "Unreal %", "Weight",
]]

holdings_styled = (
    holdings_df.style
    .map(color_signed, subset=["Day %", "Unreal P&L", "Unreal %"])
    .set_properties(**{
        "background-color": "#ffffff",
        "color": "#111827",
        "font-family": "JetBrains Mono, monospace",
        "font-size": "13px",
    })
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

# =========================
# SIDEBAR
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
# QUOTES + CHART
# =========================
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
        .map(color_signed, subset=["Chg%"])
        .set_properties(**{
            "background-color": "#ffffff",
            "color": "#111827",
            "font-family": "JetBrains Mono, monospace",
            "font-size": "13px",
        })
    )
    st.dataframe(styled, width="stretch", hide_index=True)

with col2:
    # Chart picker: sector dropdown OR any custom ticker
    pick_col, custom_col = st.columns([1, 1])
    with pick_col:
        selected_ticker = st.selectbox("Sector Ticker", tickers, key="chart_ticker")
    with custom_col:
        custom_ticker = st.text_input(
            "Or any ticker",
            placeholder="e.g. NVDA, AAPL, TSLA, ^GSPC",
            key="custom_ticker",
        ).strip().upper()

    # Custom input wins if provided
    chart_ticker = custom_ticker if custom_ticker else selected_ticker

    st.markdown(
        f'<div class="kicker">{period.upper()} · {chart_type}</div>'
        f'<div class="panel-title">{chart_ticker}</div>',
        unsafe_allow_html=True,
    )
    hist = get_history(chart_ticker, period=period)

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

# =========================
# FUNDAMENTALS
# =========================
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

# =========================
# TRADE LOG
# =========================
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
