import os
import yfinance as yf
from crewai.tools import tool
from tavily import TavilyClient

@tool("Tavily Search Tool")
def tavily_search(query: str):
    """A search tool that uses Tavily to perform web searches."""
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily.search(query=query)
    return str(response['results'])

@tool("yFinance Stock Data Tool")
def yfinance_data(ticker: str):
    """Fetches stock data for a given symbol using yfinance."""
    stock = yf.Ticker(ticker)
    return str(stock.info)