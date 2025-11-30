import yfinance as yf

def financial_data_tool(ticker: str):
    """Récupération des données financières via yfinance."""
    asset = yf.Ticker(ticker)
    info = asset.info

    return {
        "current_price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "beta": info.get("beta"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "long_business_summary": info.get("longBusinessSummary"),
    }