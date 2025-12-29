import yfinance as yf
from src.antigravity.tools import tool

@tool
async def get_market_risk_sentiment():
    """
    Fetches Market Risk Sentiment indicators:
    - VIX (Volatility Index) - Proxy for fear (High VIX often correlates with High Put/Call Ratio)
    - S&P 500 Volume (Market participation)
    """
    try:
        # Fetch VIX, S&P 500 (^GSPC), High Yield (HYG), Treasuries (TLT)
        tickers = yf.Tickers("^VIX ^GSPC HYG TLT")
        
        # Get latest day's data
        hist = tickers.history(period="1d")
        
        result = {
            "indicator": "Market Risk Sentiment",
            "vix": None, 
            "sp500_volume": None,
            "risk_ratio": None
        }

        # Safe extraction
        if "^VIX" in hist['Close']:
             result["vix"] = round(hist['Close']["^VIX"].iloc[-1], 2)
        if "^GSPC" in hist['Volume']:
             result["sp500_volume"] = int(hist['Volume']["^GSPC"].iloc[-1])
             
        # Risk Ratio (HYG / TLT)
        if "HYG" in hist['Close'] and "TLT" in hist['Close']:
             hyg = hist['Close']["HYG"].iloc[-1]
             tlt = hist['Close']["TLT"].iloc[-1]
             ratio = hyg / tlt
             result["risk_ratio"] = round(ratio, 4)
             result["hyg_price"] = round(hyg, 2)
        
        return result
    except Exception as e:
        return {"error": f"Failed to fetch market data: {str(e)}"}

@tool
async def get_market_history():
    """
    Fetches 5-year history for Market Risk indicators: VIX, HYG, TLT.
    Returns dict with 'Date', 'VIX', 'HYG', 'TLT'.
    """
    try:
        tickers = yf.Tickers("^VIX HYG TLT")
        hist = tickers.history(period="5y")
        
        if hist.empty: return {}
        
        hist = hist.reset_index()
        data = {
            "Date": [d.strftime('%Y-%m-%d') for d in hist['Date']],
            "VIX": [],
            "HYG": [],
            "TLT": [],
            "RiskRatio": []
        }
        
        closes = hist['Close']
        if "^VIX" in closes: 
            data["VIX"] = closes["^VIX"].fillna(method='ffill').tolist()
            
        if "HYG" in closes and "TLT" in closes:
            hyg = closes["HYG"].fillna(method='ffill')
            tlt = closes["TLT"].fillna(method='ffill')
            data["HYG"] = hyg.tolist()
            data["TLT"] = tlt.tolist()
            # Calculate Ratio Series
            data["RiskRatio"] = (hyg / tlt).tolist()
            
        return data
    except Exception:
        return {}

@tool
async def get_sector_history():
    """
    Fetches 5-year price history for Major Sectors.
    Sectors: XLK (Tech), XLE (Energy), XLP (Staples), XLU (Utilities), XLV (Health), XLY (Discretionary), XLI (Industrials), SPY (Market).
    Returns dict for separate columns.
    """
    try:
        symbols = "XLK XLE XLP XLU XLV XLY XLI SPY"
        tickers = yf.Tickers(symbols)
        hist = tickers.history(period="5y")
        
        if hist.empty: return {}
        
        hist = hist.reset_index()
        data = {"Date": [d.strftime('%Y-%m-%d') for d in hist['Date']]}
        
        closes = hist['Close']
        for sym in symbols.split():
            if sym in closes:
                data[sym] = closes[sym].fillna(method='ffill').tolist()
                
        return data
    except Exception:
        return {}

@tool
async def get_sector_performance():
    """
    Fetches recent performance (1 Month) for Sector analysis.
    Useful for detecting rotation (e.g. Defensive vs Growth).
    Returns dict of {Sector: 1mo_pct_change}.
    """
    try:
        symbols = "XLK XLE XLP XLU XLV XLY XLI SPY"
        tickers = yf.Tickers(symbols)
        # Fetch enough days for ~1 month (22 trading days)
        hist = tickers.history(period="2mo")
        
        if hist.empty: return {}
        
        closes = hist['Close']
        results = {}
        
        for sym in symbols.split():
             if sym in closes:
                 series = closes[sym].dropna()
                 if len(series) > 20:
                     # Approx 1 month return
                     latest = series.iloc[-1]
                     prev = series.iloc[-22] 
                     pct = ((latest - prev) / prev) * 100
                     results[sym] = round(pct, 2)
        return results
    except Exception as e:
        return {"error": str(e)}
