import yfinance as yf
import pandas as pd
from typing import Dict, Any

from src.antigravity.tools import tool

@tool
async def get_crypto_prices(tickers: list = ["BTC-USD", "ETH-USD"]) -> Dict[str, Any]:
    """
    Fetches current price and 7d trend for Crypto assets.
    """
    results = {}
    try:
        # Fetch data (1mo to calculate trends if needed, but 5d is standard for our report)
        data = yf.download(tickers, period="5d", interval="1d", progress=False)
        
        # Handle multi-index columns if multiple tickers
        if len(tickers) > 1:
            closes = data['Close']
        else:
            closes = pd.DataFrame({tickers[0]: data['Close']})

        for ticker in tickers:
            try:
                # Extract series
                series = closes[ticker].dropna()
                if series.empty:
                    results[ticker] = {"error": "No data"}
                    continue
                
                current_price = series.iloc[-1]
                start_price = series.iloc[0]
                pct_change = ((current_price - start_price) / start_price) * 100
                
                results[ticker] = {
                    "price": round(current_price, 2),
                    "5d_change_pct": round(pct_change, 2),
                    "trend": "Bullish" if pct_change > 0 else "Bearish"
                }
            except Exception as e:
                results[ticker] = {"error": str(e)}
                
        return {"crypto": results}
        
    except Exception as e:
        return {"error": f"Failed to fetch crypto: {str(e)}"}

@tool
async def get_global_indices() -> Dict[str, Any]:
    """
    Fetches major global ETFs to detect divergences.
    EZU: Eurozone
    EWJ: Japan
    EEM: Emerging Markets
    """
    tickers = ["EZU", "EWJ", "EEM", "SPY"] # SPY for comparison
    results = {}
    try:
        data = yf.download(tickers, period="5d", interval="1d", progress=False)
        closes = data['Close']
        
        for ticker in tickers:
            if ticker not in closes.columns: continue
            
            series = closes[ticker].dropna()
            if series.empty: continue
            
            current = series.iloc[-1]
            start = series.iloc[0]
            change = ((current - start) / start) * 100
            
            results[ticker] = {
                "price": round(current, 2),
                "5d_change_pct": round(change, 2)
            }
            
        return {"global_markets": results}
        
    except Exception as e:
        return {"error": f"Failed to fetch global markets: {str(e)}"}

async def get_global_history(ticker: str, period: str = "2y") -> list:
    """
    Fetches historical data for plotting.
    """
    try:
        df = yf.Ticker(ticker).history(period=period)
        df = df.reset_index()
        # Convert to list of dicts or return specific format
        # Dashboard expects list of dicts with 'Date' and 'value' (or similar)
        # Actually plot_metric handles DataFrames with Date column.
        # But get_fred_history returns list of dicts. Let's return list of dicts to be consistent.
        
        results = []
        for index, row in df.iterrows():
            results.append({
                "Date": row['Date'].strftime('%Y-%m-%d'),
                "value": row['Close']
            })
        return results
    except:
        return []
