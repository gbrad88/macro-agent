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

# ... (Previous Code) ...

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
