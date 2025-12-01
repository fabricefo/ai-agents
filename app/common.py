# scripts/_common.py
import os
import time
from openai import OpenAI
import yfinance as yf

# Initialise client OpenAI (utilise OPENAI_API_KEY dans l'environnement)
openai_client = OpenAI()

# Tavily client lazy init
def get_tavily_client():
    try:
        from tavily import TavilyClient
    except Exception:
        return None
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return None
    return TavilyClient(api_key=api_key)

def fetch_financials(ticker: str):
    """Récupère un dictionnaire synthétique via yfinance."""
    try:
        asset = yf.Ticker(ticker)
        info = asset.info or {}
    except Exception:
        info = {}

    return {
        "ticker": ticker,
        "current_price": info.get("currentPrice"),
        "market_cap": info.get("marketCap"),
        "sector": info.get("sector"),
        "beta": info.get("beta"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "long_business_summary": info.get("longBusinessSummary"),
    }

def fetch_news_tavily(query: str, max_results: int = 5):
    tavily = get_tavily_client()
    if tavily is None:
        return f"(Tavily indisponible — pas de résultats)."
    try:
        hits = tavily.search(query=query, max_results=max_results)
        # hits returned as list/dict depending on SDK – try safe formatting
        return hits
    except Exception as e:
        return f"(Erreur Tavily: {e})"

def call_llm(messages, model="gpt-4o-mini", temperature=0.0):
    """
    Appelle OpenAI chat completions et renvoie (text, usage_dict).
    usage_dict = {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
    """
    start = time.perf_counter()
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    duration = time.perf_counter() - start

    # contenu
    content = ""
    try:
        content = response.choices[0].message.content
    except Exception:
        content = str(response)

    # usage
    usage = None
    try:
        u = response.usage
        usage = {
            "prompt_tokens": getattr(u, "prompt_tokens", None) or u.get("prompt_tokens"),
            "completion_tokens": getattr(u, "completion_tokens", None) or u.get("completion_tokens"),
            "total_tokens": getattr(u, "total_tokens", None) or u.get("total_tokens"),
        }
    except Exception:
        # certains SDK retournent dicts, d'autres objets — essayer autre approche
        try:
            usage = {
                "prompt_tokens": response["usage"].get("prompt_tokens"),
                "completion_tokens": response["usage"].get("completion_tokens"),
                "total_tokens": response["usage"].get("total_tokens"),
            }
        except Exception:
            usage = {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}

    return content, usage, duration
