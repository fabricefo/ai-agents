import os
from langchain_groq import ChatGroq
from pydantic import SecretStr

# Handle both relative and absolute imports
try:
    from .tools import get_stock_data, get_news
    from .state import StockAnalysisState
except ImportError:
    from tools import get_stock_data, get_news
    from state import StockAnalysisState

# Initialize the LLM once here for all nodes
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=groq_api_key
) if groq_api_key else None

def research_node(state: StockAnalysisState):
    print("\n--- RESEARCHING STOCK AND NEWS ---")
    ticker = state["ticker"]
    stock_info = get_stock_data.invoke({"ticker":ticker})
    query_string = f"{ticker} stock news last quarter"
    news = get_news.invoke({"query":query_string})
    return {
        "stock_info": stock_info,
        "news_summary": news
    }

def analysis_node(state: StockAnalysisState):
    print("\n--- PERFORMING ANALYSIS ---")
    prompt = f"""
    You are a senior financial analyst. 
    Based on the following stock information and recent news, 
    provide a detailed analysis of the company's performance.

    Stock Info:
    {state.get('stock_info', 'No stock info available')}

    Recent News:
    {state.get('news_summary', 'No news available')}

    Provide key insights into its last quarter performance.
    """
    analysis = llm.invoke(prompt)
    return {"analysis": analysis.content}

def recommendation_node(state: StockAnalysisState):
    print("--- FORMULATING RECOMMENDATION ---")
    prompt = f"""
    Based on this analysis:
    {state.get('analysis', 'No analysis available')}

    Provide a clear recommendation: "BUY", "SELL", or "HOLD".
    Justify your recommendation in a concise, executive-level paragraph.
    """
    recommendation = llm.invoke(prompt)
    return {"recommendation": recommendation.content}