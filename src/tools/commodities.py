import yfinance as yf
from src.antigravity.tools import tool

@tool
async def get_metal_prices():
    """
    Fetches recent price action for key Metals to detect liquidity/deleveraging spikes.
    Assets: Gold (GC=F), Silver (SI=F), Copper (HG=F), Platinum (PL=F).
    Returns latest price and 5-day percent change.
    """
    try:
        # Gold, Silver, Copper, Platinum Futures
        tickers = yf.Tickers("GC=F SI=F HG=F PL=F")
        
        # Get 5 days history to check for volatility/spikes
        hist = tickers.history(period="5d")
        
        result = {
            "indicator": "Metal Commodities",
            "metals": {}
        }
        
        # Process each metal
        for symbol, name in [("GC=F", "Gold"), ("SI=F", "Silver"), ("HG=F", "Copper"), ("PL=F", "Platinum")]:
            try:
                closes = hist['Close'][symbol]
                if not closes.empty:
                    latest = closes.iloc[-1]
                    prev_5d = closes.iloc[0]
                    # Calc % change
                    pct_change = ((latest - prev_5d) / prev_5d) * 100
                    
                    result["metals"][name] = {
                        "price": round(latest, 2),
                        "5d_change_pct": round(pct_change, 2)
                    }
            except KeyError:
                continue # Symbol might be missing in df if fetch failed
                
        return result

    except Exception as e:
        return {"error": f"Failed to fetch metals data: {str(e)}"}

@tool
async def get_metal_history():
    """
    Fetches 5-year price history for Gold, Silver, Copper, Platinum.
    Returns a dict with 'dates' and separate lists for each metal prices.
    """
    try:
        tickers = yf.Tickers("GC=F SI=F HG=F PL=F")
        hist = tickers.history(period="5y")
        
        # yfinance returns a MultiIndex column DataFrame if multiple tickers
        # We need to flatten this for creating simple structure
        
        if hist.empty:
            return {}

        # Reset index to get Date as column
        hist = hist.reset_index()
        
        data = {
            "Date": [d.strftime('%Y-%m-%d') for d in hist['Date']],
            "Gold": [],
            "Silver": [],
            "Copper": [],
            "Platinum": []
        }
        
        # Safe extraction (some days might be missing values, fill fwd/bwd or 0)
        # We'll just take 'Close'
        closes = hist['Close']
        
        if "GC=F" in closes: data["Gold"] = closes["GC=F"].fillna(method='ffill').tolist()
        if "SI=F" in closes: data["Silver"] = closes["SI=F"].fillna(method='ffill').tolist()
        if "HG=F" in closes: data["Copper"] = closes["HG=F"].fillna(method='ffill').tolist()
        if "PL=F" in closes: data["Platinum"] = closes["PL=F"].fillna(method='ffill').tolist()
        
        return data

    except Exception:
        return {}
