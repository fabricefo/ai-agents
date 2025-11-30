import os
import yfinance as yf
from langchain_community.tools import tool
from tavily import TavilyClient

@tool
def get_stock_data(ticker: str):
    """Fetches stock data for a given ticker symbol using yfinance."""
    stock = yf.Ticker(ticker)
    return str(stock.info)

@tool
def get_news(query: str):
    """Searches for recent news articles related to a query using Tavily."""
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily.search(query=query)
    return str(response['results'])