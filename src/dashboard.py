import streamlit as st
import asyncio
import os
import sys

# --- DEFENSIVE ISOLATION (Phase 2) ---
# Ensure we deny AppData even if Streamlit reset the path
try:
    # Identify if we are running in the bundled environment
    # In cx_Freeze, sys.executable points to the .exe
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
    
    # Check if this script is within the executable's directory structure
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # If the script is relative to the exe (Portable mode), enforce isolation
    if script_dir.startswith(exe_dir) or "Downloads" in exe_dir or "Dist" in exe_dir:
        # Filter sys.path to ONLY allow paths inside the exe root
        # We intentionally EXCLUDE the User AppData/Roaming path
        clean_path = [p for p in sys.path if p.startswith(exe_dir) or p.lower().endswith('.zip')]
        
        # Ensure we didn't delete everything (sanity check)
        if len(clean_path) > 0:
            sys.path = clean_path
except:
    pass
# -------------------------------------

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from src.agents.macro_watchdog import macro_agent
from src.antigravity.core import Session

from src.tools.fred import get_fred_history, SERIES_MAP
from src.tools.finra import get_margin_debt_history
from src.tools.commodities import get_metal_history
from src.tools.options import get_market_history, get_sector_history, get_sector_performance
from src.tools.global_markets import get_global_history
import pandas as pd
import altair as alt

st.set_page_config(page_title="Macro Watchdog", page_icon="📉", layout="wide")

# --- UI POLISH (Phase 21) ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load the custom CSS if it exists
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    load_css(css_path)

# --- END UI POLISH ---

st.title("📉 Macro Watchdog Agent")
st.markdown("### Contrarian Economic Analysis")

# Helper for Dynamic Charts (Fixes "Straight Line" issue)
def plot_metric(df, title, color='#29b5e8'):
    if df.empty:
        st.warning(f"No data for {title}")
        return
    
    # Reset index to make Date a column for Altair
    if 'Date' not in df.columns:
        df = df.reset_index()
        # Ensure first column is named Date (reset_index might give it 'index' or None)
        df.columns = ['Date'] + list(df.columns[1:])
    
    # Identify value column (usually the remaining float column)
    val_col = [c for c in df.columns if c != 'Date'][0]
    
    chart = alt.Chart(df).mark_line(color=color).encode(
        x='Date:T',
        y=alt.Y(f'{val_col}:Q', scale=alt.Scale(zero=False), title=title),
        tooltip=['Date', val_col]
    ).properties(
        height=300
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

if st.button("Run Daily Audit"):
    with st.spinner("Agent is analyzing markets..."):
        # 1. Run the textual Agent Audit
        async def run_audit():
             session = await Session.start(agent=macro_agent)
             prompt = """
             Perform the daily macro audit:
             1. Fetch current US Debt-to-GDP (GFDEGDQ188S).
             2. Fetch Liquidity: M2 Money Supply (M2SL) and Reverse Repo (RRPONTSYD).
             3. Fetch Fed Funds Rate (FEDFUNDS) and Industrial Production (INDPRO).
             4. Fetch latest FINRA Margin Debt.
             5. Fetch Market Risk Sentiment (VIX).
             6. Fetch Copper/Gold/Silver/Platinum prices to check for deleveraging spikes.
             7. Fetch Sector Performance (1 Month).
             8. Fetch Global (EZU, EWJ, EEM) and Crypto (BTC, ETH) data.
             9. Provide a summary of the 'Macro Health Score' and 'Sector Rotation'.
             """
             return await session.ask(prompt)

        try:
            response = asyncio.run(run_audit())
            st.success("Audit Complete!")
            st.markdown("---")
            # Use st.info or st.markdown to allow text wrapping for long sentences
            st.markdown(response.text)
            st.markdown("---")
            
        except Exception as e:
            st.error(f"Error running agent: {e}")

    # 2. Visualization Section
    st.markdown("## 📊 Macro Dashboard (5 Year Trends)")
    
    # helper for creating chart df
    def make_chart_df(hist_data, col_name='value'):
        if not hist_data: return pd.DataFrame()
        df = pd.DataFrame(hist_data)
        if 'date' in df.columns: df.set_index('date', inplace=True)
        if 'Date' in df.columns: 
             df['Date'] = pd.to_datetime(df['Date'])
             df.set_index('Date', inplace=True)
        return df

    # TABS
    tab_us, tab_global = st.tabs(["🇺🇸 US Macro", "🌍 Global & Crypto"])

    with tab_us:
        # --- ROW 1: CORE ECONOMY ---
        st.subheader("1. US Economic Core")
        c1, c2 = st.columns(2)
        with c1:
            st.caption("US Debt-to-GDP Ratio (%)")
            df = make_chart_df(asyncio.run(get_fred_history("GFDEGDQ188S", limit=20))) # Quarterly 5y
            plot_metric(df, "Debt/GDP", color="#FF5A5F")
            
        with c2:
            st.caption("Industrial Production Index")
            df = make_chart_df(asyncio.run(get_fred_history("INDPRO", limit=60))) # Monthly 5y
            plot_metric(df, "IndPro", color="#00C781")

        # --- ROW 2: LIQUIDITY PLUMBING ---
        st.subheader("2. System Liquidity")
        c3, c4 = st.columns(2)
        with c3:
            st.caption("M2 Money Supply ($ Billions)")
            df = make_chart_df(asyncio.run(get_fred_history("M2SL", limit=60))) # Monthly 5y
            plot_metric(df, "M2", color="#3B8ED0")
            
        with c4:
            st.caption("Reverse Repo Overnight Volume ($ Billions)")
            df = make_chart_df(asyncio.run(get_fred_history("RRPONTSYD", limit=1250))) # Daily 5y approx
            plot_metric(df, "RRP", color="#E040FB")


        # --- ROW 3: RECESSION WATCH (NEW) ---
        st.subheader("3. Economic Cycle Risk (Recession Watch)")
        c7, c8, c9 = st.columns(3)
        with c7:
             st.caption("Yield Curve (10Y-2Y Spread)")
             st.markdown("*Negative = Inversion (Danger)*")
             df = make_chart_df(asyncio.run(get_fred_history("T10Y2Y", limit=1250)))
             plot_metric(df, "Yield Curve", color="#FF9100")
             
        with c8:
             st.caption("Consumer Sentiment (U of Mich)")
             st.markdown("*< 60 = Extreme Fear*")
             df = make_chart_df(asyncio.run(get_fred_history("UMCSENT", limit=60)))
             plot_metric(df, "Sentiment", color="#2962FF")

        with c9:
             st.caption("Unemployment Rate (%)")
             st.markdown("*Rising Baseline = Recession Trend*")
             df = make_chart_df(asyncio.run(get_fred_history("UNRATE", limit=60)))
             plot_metric(df, "Unemployment", color="#D50000")

        # --- ROW 4: HOUSING MARKET (NEW) ---
        st.subheader("4. Housing Market (Leading Indicator)")
        c10, c11 = st.columns(2)
        with c10:
             st.caption("Housing Starts (Millions)")
             st.markdown("*Cycle Highs = Bullish, Crashing = Recession*")
             df_houst = make_chart_df(asyncio.run(get_fred_history("HOUST", limit=60)))
             plot_metric(df_houst, "Housing Starts", color="#795548")
             
        with c11:
             st.caption("30-Year Fixed Mortgage Rate (%)")
             st.markdown("*Inverse correlation to Affordability*")
             df_mort = make_chart_df(asyncio.run(get_fred_history("MORTGAGE30US", limit=250)))
             plot_metric(df_mort, "Mortgage Rate", color="#607D8B")

        # --- ROW 5: RISK APPETITE ---
        st.subheader("5. Risk Appetite & Sentiment")
        # Fetch Market Data once
        mkt_data = asyncio.run(get_market_history())
        
        c5, c6, c_finra = st.columns(3)
        with c5:
             st.caption("VIX (Fear Index)")
             if mkt_data and "VIX" in mkt_data:
                 df_vix = pd.DataFrame({"VIX": mkt_data["VIX"]}, index=pd.to_datetime(mkt_data["Date"]))
                 plot_metric(df_vix, "VIX", color="#FF5A5F")
                 
        with c6:
             st.caption("Credit Risk Appetite (HYG / TLT Ratio)")
             st.markdown("*Rising = Bullish (Risk On), Falling = Defensive*")
             if mkt_data and "RiskRatio" in mkt_data:
                 df_ratio = pd.DataFrame({"HYG/TLT": mkt_data["RiskRatio"]}, index=pd.to_datetime(mkt_data["Date"]))
                 plot_metric(df_ratio, "Risk Ratio", color="#00C781")
                 
        with c_finra:
             st.caption("FINRA Margin Debt ($ Millions)")
             st.markdown("*Rising = Leveraged Upside, Falling = Deleveraging*")
             finra_hist = asyncio.run(get_margin_debt_history(limit=60))
             df_finra = make_chart_df(finra_hist)
             plot_metric(df_finra, "Margin Debt", color="#6200EA")

        # --- ROW 6: SECTORS ---
        st.subheader("6. Sector Rotation")
        sectors_hist = asyncio.run(get_sector_history())
        if sectors_hist and "Date" in sectors_hist:
             df_sectors = pd.DataFrame(sectors_hist)
             if 'Date' in df_sectors.columns:
                 df_sectors['Date'] = pd.to_datetime(df_sectors['Date'])
                 df_sectors.set_index('Date', inplace=True)
             
             # Normalize
             df_sec_norm = (df_sectors / df_sectors.iloc[0] - 1) * 100
             df_sec_norm = df_sec_norm.reset_index()
             
             df_melt = df_sec_norm.melt('Date', var_name='Sector', value_name='Return%')
             
             chart = alt.Chart(df_melt).mark_line().encode(
                 x='Date:T',
                 y='Return%:Q',
                 color='Sector:N',
                 tooltip=['Date', 'Sector', 'Return%']
             ).properties(height=400, title="Sector Performance vs SPY (5 Years)").interactive()
             
             st.altair_chart(chart, use_container_width=True)


    with tab_global:
        st.subheader("⚡ Crypto-Currency (Risk Gauge)")
        g1, g2 = st.columns(2)
        with g1:
            st.caption("Bitcoin (BTC-USD)")
            df_btc = make_chart_df(asyncio.run(get_global_history("BTC-USD", period="2y")))
            plot_metric(df_btc, "Bitcoin", color="#F7931A")
        with g2:
            st.caption("Ethereum (ETH-USD)")
            df_eth = make_chart_df(asyncio.run(get_global_history("ETH-USD", period="2y")))
            plot_metric(df_eth, "Ethereum", color="#627EEA")

        st.subheader("🌍 Global Market Divergence")
        g3, g4, g5 = st.columns(3)
        with g3:
            st.caption("Europe (EZU)")
            plot_metric(make_chart_df(asyncio.run(get_global_history("EZU", period="2y"))), "Europe", color="#003399")
        with g4:
            st.caption("Japan (EWJ)")
            plot_metric(make_chart_df(asyncio.run(get_global_history("EWJ", period="2y"))), "Japan", color="#BC002D")
        with g5:
            st.caption("Emerging Markets (EEM)")
            plot_metric(make_chart_df(asyncio.run(get_global_history("EEM", period="2y"))), "Emerging", color="#FFC107")


    st.info("Check `d:\\projects\\economic_indicators\\src\\main.py` for CLI version.")
