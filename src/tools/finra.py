import pandas as pd
from src.antigravity.tools import tool
import logging

def _fetch_finra_data():
    """Helper to fetch and clean FINRA data"""
    url = "https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics"
    try:
        # pandas read_html returns a list of dataframes
        dfs = pd.read_html(url)
        
        target_df = None
        for df in dfs:
            # Look for the relevant column header
            if any("Debit Balances" in str(col) for col in df.columns):
                target_df = df
                break
        
        if target_df is None:
            return None

        # Clean up column names
        # Identify the Debit Column and Date Column
        debit_col = [c for c in target_df.columns if "Debit Balances" in str(c)][0]
        date_col = [c for c in target_df.columns if "Month" in str(c) or "Year" in str(c)][0]
        
        # Renaissance the dataframe
        clean_df = target_df[[date_col, debit_col]].copy()
        clean_df.columns = ["Date", "DebitBalances"]
        
        # Debug: Print first few raw dates
        # print(f"DEBUG RAW DATES: {clean_df['Date'].head().tolist()}")
        
        # Explicitly invoke to_datetime with format if possible, or robustly handle it
        # usually FINRA uses "Jan-24", "Feb-24" etc. (%b-%y)
        try:
             clean_df["Date"] = pd.to_datetime(clean_df["Date"], format="%b-%y")
        except:
             # Fallback to default
             clean_df["Date"] = pd.to_datetime(clean_df["Date"], errors='coerce')
        
        clean_df = clean_df.dropna().sort_values("Date", ascending=False)
        
        if clean_df.empty:
            logging.error("Dataframe empty after date parsing.")
            return None
            
        return clean_df
            
    except Exception as e:
        logging.error(f"Error fetching FINRA data: {e}")
        # print(f"DEBUG ERROR: {e}")
        return None

@tool
async def get_margin_debt(limit: int = 1):
    """
    Fetches the latest Margin Debt statistics from FINRA.
    Returns the latest 'Debit Balances in Customers' Securities Margin Accounts'.
    """
    df = _fetch_finra_data()
    
    if df is not None and not df.empty:
        latest = df.iloc[0]
        return {
            "indicator": "FINRA Margin Debt",
            "value": int(latest["DebitBalances"]),
            "date": latest["Date"].strftime("%Y-%m-%d"),
            "note": "Value in Millions"
        }
    else:
        return {"error": "Could not fetch Margin Statistics from FINRA."}

async def get_margin_debt_history(limit: int = 60):
    """
    Returns historical margin debt data for plotting.
    Limit defaults to 5 years (60 months).
    """
    df = _fetch_finra_data()
    if df is not None:
        # Sort ascending for charts
        df = df.sort_values("Date", ascending=True)
        # return last N records
        return df.tail(limit).to_dict(orient="records")
    return []
