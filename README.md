# 🦅 Antigravity Macro Agent

**AI-Powered US Economic Monitoring Dashboard**

The **Antigravity Macro Agent** is an autonomous system that monitors, analyzes, and interprets critical US economic data. Unlike standard dashboards that just show charts, this Agent uses heuristic logic ("MacroWatchdog") to assess Recession Risk, Liquidity Stress, and Market Sentiment, providing actionable "Insights" and "Strategic Outlooks" in plain English.

---

## ⚡ Easy Installation

**No coding knowledge required.** Follow these exact steps:

### Step 1: Download
1.  Look at the top-right of this page for the green **< > Code** button.
2.  Click it to open the dropdown menu.
3.  Select **Download ZIP** from the list.

### Step 2: Extract
1.  Find the `macro-agent-main.zip` file in your Downloads folder.
2.  Right-click it and select **Extract All...**
3.  Extract it to a clean folder (like your Desktop).

### Step 3: Run
1.  Open the extracted folder.
2.  Double-click the file named `launcher.bat`.
3.  **SETUP**: The first time you run it, you will be asked for a **FRED API Key**.
    *   **[Click Here to Get a Free API Key](https://fred.stlouisfed.org/docs/api/api_key.html)**
    *   Paste it into the black window when asked and press Enter.
4.  **Wait**: It will install the AI tools (approx 1 min).
5.  The Dashboard will automatically open in your browser.

*Note: You only need [Python](https://www.python.org/downloads/) installed on your computer.*

---

## 🚀 Key Features

### 1. 🧠 AI-Driven Analysis
- **Narrative Generation**: Automatically converts raw data into sentence-based insights (e.g., *"The Yield Curve is Inverted (-0.15), warning of potential recession"*).
- **Macro Health Score**: Aggregates 15+ metrics into a single score (-5 to +5) to determine the market regime (Risk-On vs. Risk-Off).
- **Strategic Advice**: Suggests ETF allocations (e.g., *"Shift to Utilities (XLU)"*) based on the cycle.

### 2. 📊 Comprehensive Data Coverage
- **Core Economy**: Debt-to-GDP, Industrial Production.
- **Liquidity**: M2 Money Supply, Reverse Repo (RRP) "Plumbing".
- **Recession Watch**: 10Y-2Y Yield Curve, Sahm Rule (Unemployment), Consumer Sentiment.
- **Housing**: Mortgage Rates (30Y Fixed) vs. Housing Starts.
- **Market Risk**: VIX Term Structure, **Margin Debt**, Put/Call Ratios.
- **Commodities**: Gold, Copper, Platinum prices (Inflation signals).

### 3. 🖥️ Interactive Dashboard
- Built with **Streamlit** + **Altair**.
- **Dynamic 5-Year Charts**: User-selectable history.
- **Sector Overlay**: Normalizes performance of Spy/Tech/Energy/Utilities/Industrials on one chart.

---

## 🛠️ Developer Setup (Manual)

### Prerequisites
- Python 3.9+
- A [FRED API Key](https://fred.stlouisfed.org/docs/api/api_key.html) (Free).

### Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/gbrad88/macro-agent.git
    cd macro-agent
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    FRED_API_KEY=your_actual_api_key_here
    ```

---

## ▶️ Usage

### Quick Start (Windows)
Double-click the `run_dashboard.bat` file.

### Manual Start
```bash
streamlit run src/dashboard.py
```

---

## 📂 Project Structure

- `src/agents/`: Logic for the AI Analyst (`MacroWatchdog`).
- `src/tools/`: Data fetchers for FRED, Yahoo Finance, Finra.
- `src/antigravity/`: Core agent framework.
- `src/dashboard.py`: The Streamlit frontend.

---

## 📜 License
MIT
