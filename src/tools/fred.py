import os
import httpx
from src.antigravity.tools import tool

# API Key handling
FRED_API_KEY = os.environ.get("FRED_API_KEY")

# Friendly names for common series
SERIES_MAP = {
    'GFDEGDQ188S': 'US Debt-to-GDP Ratio (%)',
    'FEDFUNDS': 'Fed Funds Rate (%)',
    'INDPRO': 'Industrial Production Index',
    'M2SL': 'M2 Money Supply ($ Billions)',
    'RRPONTSYD': 'Reverse Repo Volume ($ Billions)',
    'T10Y2Y': '10-Year minus 2-Year Treasury Spread',
    'UMCSENT': 'Consumer Sentiment (Univ. of Michigan)',
    'UNRATE': 'Unemployment Rate (%)',
    'HOUST': 'Housing Starts (New Privately Owned)',
    'MORTGAGE30US': '30-Year Fixed Rate Mortgage Average'
}

@tool
async def get_macro_indicator(series_id: str):
    """
    Fetches the latest value for a specific FRED series.
    """
    if not FRED_API_KEY:
        return {"error": "FRED_API_KEY not found. Please set environment variable."}

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'observations' in data and data['observations']:
                obs = data['observations'][0]
                readable_name = SERIES_MAP.get(series_id, series_id)
                return {
                    "indicator": readable_name, 
                    "value": obs['value'], 
                    "date": obs['date']
                }
            else:
                return {"error": f"No observations found for {series_id}"}
        except Exception as e:
            return {"error": f"Failed to fetch FRED data: {str(e)}"}

@tool
async def get_fred_history(series_id: str, limit: int = 12):
    """
    Fetches historical data for a FRED series. 
    Default limit 12 (approx 1 year for monthly data).
    Returns a list of dicts: {'date': 'YYYY-MM-DD', 'value': float}.
    """
    if not FRED_API_KEY:
        return []

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            history = []
            if 'observations' in data:
                # Observations come in desc order (newest first)
                # We want them sorted by date for charting
                obs_list = sorted(data['observations'], key=lambda x: x['date'])
                
                for obs in obs_list:
                    try:
                        val = float(obs['value'])
                        history.append({'date': obs['date'], 'value': val})
                    except ValueError:
                        continue # Skip "." or invalid values
            
            return history
        except Exception as e:
            return []
                

