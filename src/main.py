import asyncio
import os
import sys

# Add project root to path to ensure imports work if run from nested dirs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from src.agents.macro_watchdog import macro_agent
from src.antigravity.core import Session

async def run_daily_macro_report():
    print("--- Starting Daily Macro Audit ---")
    
    # Check for API Key
    if not os.environ.get("FRED_API_KEY"):
        print("WARNING: FRED_API_KEY not found in environment.")
        print("Data fetching tools will return errors.")

    # 1. Start the session
    session = await Session.start(agent=macro_agent)
    
    # 2. Ask the agent to perform the daily audit
    prompt = """
    Perform the daily macro audit:
    1. Fetch current US Debt-to-GDP (GFDEGDQ188S).
    2. Fetch Liquidity: M2 Money Supply (M2SL) and Reverse Repo (RRPONTSYD).
    3. Fetch Fed Funds Rate (FEDFUNDS) and Industrial Production (INDPRO).
    4. Fetch Housing Data: Starts (HOUST) and Mortgage Rates (MORTGAGE30US).
    5. Fetch Recession Signals: Yield Curve (T10Y2Y), Sentiment (UMCSENT), Unemployment (UNRATE).
    6. Fetch latest FINRA Margin Debt and Market Risk Sentiment (VIX).
    7. Fetch Copper/Gold/Silver/Platinum prices.
    8. Fetch Sector Performance (1 Month).
    9. Fetch Global (EZU, EWJ, EEM) and Crypto (BTC, ETH) data.
    10. Provide a summary of 'Macro Health', 'Housing Stress', and 'Recession Risk'.
    11. BASED ON THE SCORE, PROVIDE ETF SECTOR RECOMMENDATIONS.
    """
    
    response = await session.ask(prompt)
    print(f"\nDAILY MACRO REPORT:\n{response.text}")
    print("--- Audit Complete ---")

if __name__ == "__main__":
    asyncio.run(run_daily_macro_report())
