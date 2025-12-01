# scripts/adk_script.py
"""
ADK implementation for the 3-agent stock analysis workflow.

Install:
  pip install openai tavily-python yfinance adk

Environment variables:
  OPENAI_API_KEY
  TAVILY_API_KEY (optional)

Usage:
  from adk_script import run_adk
  res = run_adk("AAPL")
"""

import os
import time
import json
from typing import Dict, Any

import yfinance as yf
from openai import OpenAI

# Try import ADK SDK
try:
    from adk import AgentPipeline, Tool  # optional, for semantic clarity
    HAS_ADK = True
except Exception:
    HAS_ADK = False

# Tavily optional
try:
    from tavily import TavilyClient
except Exception:
    TavilyClient = None

# ---------- CONFIG ----------
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_CLIENT = OpenAI()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
TAVILY_CLIENT = None
if TavilyClient and TAVILY_API_KEY:
    try:
        TAVILY_CLIENT = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception:
        TAVILY_CLIENT = None

# ---------- UTIL ----------

def safe_get_usage(resp: Any) -> Dict[str, Any]:
    usage = {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    try:
        u = getattr(resp, "usage", None) or (resp.get("usage") if isinstance(resp, dict) else None)
        if not u:
            return usage
        usage["prompt_tokens"] = getattr(u, "prompt_tokens", u.get("prompt_tokens", None))
        usage["completion_tokens"] = getattr(u, "completion_tokens", u.get("completion_tokens", None))
        usage["total_tokens"] = getattr(u, "total_tokens", u.get("total_tokens", None))
    except Exception:
        pass
    return usage

def call_llm(messages):
    start = time.perf_counter()
    resp = OPENAI_CLIENT.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.0,
    )
    duration = time.perf_counter() - start
    try:
        text = resp.choices[0].message.content
    except:
        text = str(resp)
    usage = safe_get_usage(resp)
    return text, usage, round(duration, 3), resp

# ---------- TOOLS ----------

def yf_fetch(ticker: str) -> Dict[str, Any]:
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        return {
            "ticker": ticker,
            "shortName": info.get("shortName"),
            "currentPrice": info.get("currentPrice"),
            "marketCap": info.get("marketCap"),
            "sector": info.get("sector"),
            "beta": info.get("beta"),
            "52WeekHigh": info.get("fiftyTwoWeekHigh"),
            "52WeekLow": info.get("fiftyTwoWeekLow"),
            "longBusinessSummary": info.get("longBusinessSummary"),
        }
    except Exception as e:
        return {"error": f"yfinance error: {e}"}

def tavily_search(ticker: str, max_results: int = 5):
    if TAVILY_CLIENT is None:
        return "(Tavily unavailable - set TAVILY_API_KEY)"
    try:
        return TAVILY_CLIENT.search(query=f"{ticker} stock news", max_results=max_results)
    except Exception as e:
        return f"(Tavily error: {e})"

# ---------- Prompt templates ----------

RESEARCH_PROMPT_TEMPLATE = """
You are research_analyst.
Gather key news and financial facts for the ticker: {ticker}.

YFinance summary:
{yfinance_json}

Tavily news:
{tavily_json}

Output:
1) Top headlines
2) Financial highlights
3) Potential risks
4) Initial observations
"""

STRATEGY_PROMPT_TEMPLATE = """
You are investment_strategist.
Based on the research below, provide:
- Concise fundamental analysis
- Top 3 risks
- Top 3 opportunities
- Buy/Hold/Sell recommendation with rationale

Research:
{research_text}
"""

REPORT_PROMPT_TEMPLATE = """
You are report_writer.
Compose a final structured investment report.

Include:
1) Executive summary
2) Key findings from research
3) Strategy & recommendation
4) Conclusion

Research:
{research_text}

Strategy:
{strategy_text}
"""

# ---------- Runner ----------

def run_adk(ticker: str) -> Dict[str, Any]:
    t0 = time.time()

    # 1) research
    fin = yf_fetch(ticker)
    news = tavily_search(ticker)
    research_prompt = RESEARCH_PROMPT_TEMPLATE.format(
        ticker=ticker,
        yfinance_json=json.dumps(fin, indent=2, ensure_ascii=False),
        tavily_json=json.dumps(news, indent=2, ensure_ascii=False) if not isinstance(news, str) else news
    )
    research_messages = [
        {"role": "system", "content": "You are an experienced financial research analyst."},
        {"role": "user", "content": research_prompt}
    ]
    r_text, r_usage, r_dur, r_raw = call_llm(research_messages)

    # 2) strategy
    strategy_prompt = STRATEGY_PROMPT_TEMPLATE.format(research_text=r_text)
    strategy_messages = [
        {"role": "system", "content": "You are a seasoned investment strategist."},
        {"role": "user", "content": strategy_prompt}
    ]
    s_text, s_usage, s_dur, s_raw = call_llm(strategy_messages)

    # 3) report
    report_prompt = REPORT_PROMPT_TEMPLATE.format(research_text=r_text, strategy_text=s_text)
    report_messages = [
        {"role": "system", "content": "You are a professional financial report writer."},
        {"role": "user", "content": report_prompt}
    ]
    rep_text, rep_usage, rep_dur, rep_raw = call_llm(report_messages)

    total_time = round(time.time() - t0, 3)

    # aggregate tokens
    def to_int(v):
        try:
            return int(v) if v is not None else None
        except:
            return None

    input_tokens = sum(filter(None, [to_int(r_usage.get("prompt_tokens")), to_int(s_usage.get("prompt_tokens")), to_int(rep_usage.get("prompt_tokens"))])) or None
    output_tokens = sum(filter(None, [to_int(r_usage.get("completion_tokens")), to_int(s_usage.get("completion_tokens")), to_int(rep_usage.get("completion_tokens"))])) or None
    total_tokens = sum(filter(None, [to_int(r_usage.get("total_tokens")), to_int(s_usage.get("total_tokens")), to_int(rep_usage.get("total_tokens"))])) or None

    token_usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

    intermediate = {
        "research_output": r_text,
        "strategy_output": s_text,
        "report_output": rep_text
    }

    meta = {
        "agent_durations": {
            "research": r_dur,
            "strategy": s_dur,
            "report": rep_dur
        },
        "agent_tokens": {
            "research": r_usage,
            "strategy": s_usage,
            "report": rep_usage
        },
    }

    return {
        "framework": "adk",
        "ticker": ticker,
        "time_seconds": total_time,
        "token_usage": token_usage,
        "intermediate_steps": intermediate,
        "final_result": rep_text,
        "meta": meta
    }

# ---------- CLI ----------
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 ADK Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    results = run_adk(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Analysis: {results['final_result']}")
    # --------------------------------------------
    print("\n[bold blue]Token usage metrics:[/bold blue]")
    usage = results.get("token_usage")
    if usage:
        for key, value in usage.items():
            print(f"  {key.replace('_', ' ').capitalize()}: {value}")
    else:
        print("  Token usage metrics not available.")
        

