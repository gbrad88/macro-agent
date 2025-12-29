from src.antigravity.core import Agent
from src.tools.fred import get_macro_indicator
from src.tools.finra import get_margin_debt
from src.tools.options import get_market_risk_sentiment
from src.tools.commodities import get_metal_prices
from src.tools.global_markets import get_crypto_prices, get_global_indices


from typing import Dict

def analyze_macro_data(results: Dict) -> str:
    """
    Analyzes the aggregated results and returns a Health Score.
    """
    score = 0
    report = []
    
    # --- 1. DATA EXTRACTION ---
    gdp_debt = results.get("GFDEGDQ188S", {}).get("value")
    indpro = results.get("INDPRO", {}).get("value")
    m2 = results.get("M2SL", {}).get("value")
    rrp = results.get("RRPONTSYD", {}).get("value")
    houst = results.get("HOUST", {}).get("value")
    mort = results.get("MORTGAGE30US", {}).get("value")
    curve = results.get("T10Y2Y", {}).get("value")
    sent = results.get("UMCSENT", {}).get("value")
    sentiment_data = results.get("Market Sentiment", {})
    vix = sentiment_data.get("vix")
    risk_ratio = sentiment_data.get("risk_ratio")
    metals = results.get("Metals", {}).get("metals", {})

    # --- 2. SCORING LOGIC ---
    
    # Core Economy
    if gdp_debt and float(gdp_debt) > 120: score -= 2
    elif gdp_debt and float(gdp_debt) > 100: score -= 1
    
    if indpro and float(indpro) > 103: score += 1
    elif indpro and float(indpro) < 100: score -= 1

    # Liquidity
    if rrp and float(rrp) > 2000: score -= 1
    
    # Risk
    if vix:
        if float(vix) > 30: score -= 2
        elif float(vix) > 20: score -= 1
        else: score += 1

    # Credit
    if risk_ratio and risk_ratio > 1.0: score += 1
    
    # Metals (Fear Check)
    if metals:
        for name, data in metals.items():
            if data.get("5d_change_pct", 0) > 3.0: 
                score -= 1
                break

    # --- 3. SECTOR LOGIC ---
    allocations = []
    sector_notes = []
    sectors = results.get("Sector Performance", {})
    tech_mom = sectors.get("XLK", 0)
    util_mom = sectors.get("XLU", 0)
    energy_mom = sectors.get("XLE", 0)
    ind_mom = sectors.get("XLI", 0)
    spy_mom = sectors.get("SPY", 0)
    
    if sectors:
        sector_notes.append(f"Market (SPY) 1-Month Trend: {spy_mom}%")
        if tech_mom > util_mom:
            sector_notes.append(f"Risk-On Signal: Tech ({tech_mom}%) > Utilities ({util_mom}%).")
        else:
            sector_notes.append(f"Defensive Rotation: Utilities ({util_mom}%) > Tech ({tech_mom}%).")
        if ind_mom > spy_mom:
            sector_notes.append(f"Cyclical Strength: Industrials ({ind_mom}%) leading.")
            
    # Allocations
    inflation_risk = (metals and any(d.get("5d_change_pct", 0) > 3.0 for d in metals.values()))
    if inflation_risk or energy_mom > 5.0:
        allocations.append(f"🛡️ INFLATION HEDGE: Buy Gold (GLD), Energy (XLE).")
        
    if score > 0:
        if tech_mom > util_mom: allocations.append(f"🚀 GROWTH MOMENTUM: Tech (XLK), AI (NVDA).")
        if ind_mom > 0: allocations.append(f"🏭 CYCLICALS: Industrials (XLI).")
    else:
        allocations.append("🛡️ DEFENSIVE: Overweight Healthcare (XLV), Utilities (XLU).")
        
    if score < -3: allocations = ["🚨 CASH IS KING: Sell Equities, Buy T-Bills (BIL)"]
    if score > 1: allocations.append("🏠 HOUSING RECOVERY: Buy Homebuilders (ITB) if rates stabilize.")

    # --- 4. OUTPUT GENERATION (INSIGHTS) ---
    factors = []
    
    # Core Insight
    if gdp_debt and indpro:
        core_msg = f"The Core Economy is in a tug-of-war; Industrial Production ({indpro}) signals activity, but the massive Debt-to-GDP ratio ({gdp_debt}%) acts as a long-term structural drag."
        if float(indpro) > 103: core_msg = f"The Core Economy shows surprising resilience with Industrial Production at {indpro}, defying the weight of {gdp_debt}% Debt-to-GDP."
        elif float(indpro) < 100: core_msg = f"The Core Economy is buckling, with Industrial Production falling to {indpro} under the pressure of {gdp_debt}% Debt-to-GDP."
        factors.append(f"• **Core Economy**: {core_msg}")
    
    # Liquidity Insight
    liq_msg = f"System liquidity remains ample with M2 at ${m2}B, supporting asset prices."
    if rrp and float(rrp) > 1000: 
        liq_msg = f"While M2 is high, ${rrp}B is trapped in Reverse Repos, indicating banks are hoarding cash rather than lending it to the real economy."
    factors.append(f"• **Liquidity**: {liq_msg}")
    
    # Housing Insight
    if houst and mort:
        h_msg = f"The Housing market is stabilizing with {houst}k starts and rates at {mort}%."
        if float(mort) > 7.0: h_msg = f"High borrowing costs ({mort}%) are freezing the Housing market, which will likely drag on GDP in coming quarters."
        elif float(houst) > 1500: h_msg = f"Despite rates at {mort}%, Housing Starts are booming ({houst}k), suggesting strong consumer demand."
        factors.append(f"• **Housing Market**: {h_msg}")
    
    # Recession Insight
    if curve:
        c_msg = f"The Yield Curve is normal ({curve}), suggesting no immediate recessionary signal from the bond market."
        if float(curve) < 0: c_msg = f"The Yield Curve is **Inverted** ({curve}), a historically accurate warning that the continued tight policy is choking growth."
        factors.append(f"• **Yield Curve**: {c_msg}")
        
    # Sentiment/Risk Insight
    sent_msg = f"Consumer Sentiment is neutral ({sent}), while the VIX ({vix}) shows a market comfortable with current risks."
    if sent and float(sent) < 60: sent_msg = f"The consumer is deeply pessimistic (Sentiment {sent}), yet the stock market (VIX {vix}) seems ignoring this distress."
    if float(vix or 0) > 20: sent_msg = f"Fear has entered the market (VIX {vix}), aligning with weak consumer sentiment."
    factors.append(f"• **Sentiment & Risk**: {sent_msg}")
    
    # Global & Crypto Insight
    crypto = results.get("Crypto", {}).get("crypto", {})
    globe = results.get("Global Markets", {}).get("global_markets", {})
    
    if crypto and globe:
        btc_trend = crypto.get("BTC-USD", {}).get("trend", "Neutral")
        btc_change = crypto.get("BTC-USD", {}).get("5d_change_pct", 0)
        ezu_chg = globe.get("EZU", {}).get("5d_change_pct", 0)
        ewj_chg = globe.get("EWJ", {}).get("5d_change_pct", 0)
        spy_chg = globe.get("SPY", {}).get("5d_change_pct", 0)
        
        g_msg = "Global markets are moving in sync with the US."
        if spy_chg > (ezu_chg + 2.0): g_msg = "US Exceptionalism is in play; Wall St is outperforming Europe and Japan."
        elif ezu_chg > spy_chg: g_msg = "Global rotation is underway; capital is flowing into Europe/International markets."
        
        risk_msg = "quiet."
        if btc_change > 5.0: risk_msg = "screaming 'Risk-On' as Bitcoin rallies hard."
        elif btc_change < -5.0: risk_msg = "flashing warning signs as Crypto liquidity evaporates."
        
        factors.append(f"• **Global & Crypto**: {g_msg} Bitcoin is {risk_msg} ({btc_change}%)")

    # Margin Debt Insight
    margin_debt = results.get("Margin Debt", {})
    if margin_debt and "value" in margin_debt:
        md_val = margin_debt.get("value")
        factors.append(f"• **Margin Debt**: Investors are leveraging up with ${md_val}M in margin debt, a signal of high risk appetite.")
        # Simple scoring boost for "risk on" behavior, though could be contrarian signal if extreme
        score += 1

        # Modulate Allocations
        if btc_change > 5.0 and score > 0: allocations.append("⚡ CRYPTO MOMENTUM: Bitcoin (IBIT) breakout.")
        if ezu_chg > spy_chg: allocations.append("🌍 GLOBAL VALUE: Buy Europe (EZU) or Japan (EWJ).")

    # Summary Synthesis
    synthesis = "The data paints a picture of "
    path_forward = "The prudent path ahead is to "
    
    if score > 2: 
        synthesis += "a surprisingly robust expansion. Despite high rates, the industrial and housing engines are firing."
        path_forward += "ride the momentum in Growth (XLK) and Cyclicals (XLI), as the 'Soft Landing' scenario appears synonymous with 'No Landing'."
    elif score < 0:
        synthesis += "fragility. The inverted yield curve and trapped liquidity are warning signs that the credit cycle is turning."
        path_forward += "prioritize capital preservation. Shift into Defensives (XLV/XLU) and hold higher cash balances until the yield curve un-inverts."
    else:
        synthesis += "conflicting signals. We have a 'K-shaped' divergence where liquidity keeps asset prices high while the real economy (Housing/Sentiment) struggles."
        path_forward += "remain nimble. Avoid aggressive bets on either side; hedge equity exposure with Commodities (GLD) and focus on quality balance sheets."

    # Final Verdict Calculation
    health_verdict = "NEUTRAL"
    if score > 2: health_verdict = "HEALTHY (Risk-On)"
    if score < 0: health_verdict = "CAUTION (Hedge)"
    if score < -3: health_verdict = "DANGER (Risk-Off)"

    final_summary = f"{synthesis} {path_forward}"

    sector_text = ""
    if sector_notes:
        sector_text = "📊 SECTOR ANALYSIS:\n" + chr(10).join(['    - ' + s for s in sector_notes]) + "\n"

    return f"""
    🔎 FACTOR INSIGHTS:
    {chr(10).join(factors)}
    
    🧭 STRATEGIC OUTLOOK:
    {final_summary}
    
    MACRO HEALTH SCORE: {score} ({health_verdict})
    
    {sector_text}
    🤖 AI RECOMMENDATION:
    {chr(10).join(['    ' + a for a in allocations])}
    """

macro_agent = Agent(
    name="MacroWatchdog",
    instructions="Process the data using `analyze_macro_data` logic.",
    tools=[
        get_macro_indicator, 
        get_margin_debt, 
        get_market_risk_sentiment, 
        get_metal_prices,
        get_crypto_prices,
        get_global_indices
    ],
    analysis_logic=analyze_macro_data
)
