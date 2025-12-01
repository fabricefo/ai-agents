# scripts/agno_script.py
"""
Agno implementation for the 3-agent stock analysis workflow.

Install:
  pip install openai tavily-python yfinance agno

Environment variables:
  OPENAI_API_KEY
  TAVILY_API_KEY (optional)

Usage:
  from agno_script import run_agno
  res = run_agno("AAPL")
"""

import os
import time
import json
from typing import Dict, Any

import yfinance as yf
from openai import OpenAI

# Try to import Agno for semantic clarity (not required for token capture)
try:
    from agno.agent import Agent, Team  # optional - for clarity only
    HAS_AGNO = True
except Exception:
    HAS_AGNO = False

# Tavily optional
try:
    from tavily import TavilyClient
except Exception:
    TavilyClient = None

# ---------- CONFIG ----------
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_CLIENT = OpenAI()  # reads OPENAI_API_KEY from env

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
TAVILY_CLIENT = None
if TavilyClient and TAVILY_API_KEY:
    try:
        TAVILY_CLIENT = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception:
        TAVILY_CLIENT = None

# ---------- UTIL helpers ----------

def safe_get_usage(resp: Any) -> Dict[str, Any]:
    usage = {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    try:
        u = getattr(resp, "usage", None) or (resp.get("usage") if isinstance(resp, dict) else None)
        if not u:
            return usage
        # object or dict
        if hasattr(u, "prompt_tokens"):
            usage["prompt_tokens"] = int(getattr(u, "prompt_tokens", None)) if getattr(u, "prompt_tokens", None) is not None else None
            usage["completion_tokens"] = int(getattr(u, "completion_tokens", None)) if getattr(u, "completion_tokens", None) is not None else None
            usage["total_tokens"] = int(getattr(u, "total_tokens", None)) if getattr(u, "total_tokens", None) is not None else None
        else:
            usage["prompt_tokens"] = int(u.get("prompt_tokens")) if u.get("prompt_tokens") is not None else None
            usage["completion_tokens"] = int(u.get("completion_tokens")) if u.get("completion_tokens") is not None else None
            usage["total_tokens"] = int(u.get("total_tokens")) if u.get("total_tokens") is not None else None
    except Exception:
        pass
    return usage

def call_llm(messages, model=OPENAI_MODEL, temperature=0.0):
    """
    Call OpenAI chat completion and return (text, usage_dict, duration_seconds, raw_response)
    messages: list of {"role": "...", "content": "..."}
    """
    start = time.perf_counter()
    resp = OPENAI_CLIENT.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    duration = time.perf_counter() - start

    # extract text
    try:
        text = resp.choices[0].message.content
    except Exception:
        text = str(resp)

    usage = safe_get_usage(resp)
    return text, usage, round(duration, 3), resp

# ---------- Tools: yfinance & tavily ----------

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
        return "(Tavily unavailable - set TAVILY_API_KEY to enable)"
    try:
        hits = TAVILY_CLIENT.search(query=f"{ticker} stock news", max_results=max_results)
        return hits
    except Exception as e:
        return f"(Tavily error: {e})"

# ---------- Agno semantic agents (optional) ----------

if HAS_AGNO:
    research_agent = Agent(
        name="research_analyst",
        role="financial research",
        instructions="Collect Tavily + yfinance data for a ticker"
    )
    strategist_agent = Agent(
        name="investment_strategist",
        role="investment strategy",
        instructions="Analyze research results and propose strategy"
    )
    writer_agent = Agent(
        name="report_writer",
        role="report writer",
        instructions="Produce the final investor-facing report"
    )
    # Team can be declared for clarity but we do calls manually to capture tokens
    team = Team(name="StockTeam", agents=[research_agent, strategist_agent, writer_agent])


# ---------- Prompt templates (same across frameworks) ----------

RESEARCH_PROMPT_TEMPLATE = """
You are research_analyst.
Gather key news and financial facts for the ticker: {ticker}.

YFinance summary (JSON):
{yfinance_json}

Tavily news (raw):
{tavily_json}

Output a structured analysis with sections:
1) Top headlines (short)
2) Financial highlights (bullet)
3) Potential risks (bullet)
4) Initial observations (short)

Respond as plain text.
"""

STRATEGY_PROMPT_TEMPLATE = """
You are investment_strategist.
Based on the research below, provide:
- A concise fundamental analysis (1-2 paragraphs)
- Top 3 risks
- Top 3 opportunities
- A recommendation: Buy / Hold / Sell (with rationale)

Research:
{research_text}
"""

REPORT_PROMPT_TEMPLATE = """
You are report_writer.
Compose a clean final investment report from the research and strategy.
Include:
1) Executive summary (2-3 sentences)
2) Key findings from research
3) Strategy & recommendation (Buy/Hold/Sell)
4) Short conclusion & action items

Research:
{research_text}

Strategy:
{strategy_text}
"""

# ---------- Runner function (exported) ----------

def run_agno(ticker: str) -> Dict[str, Any]:
    t0 = time.time()
    # 1) research
    fin = yf_fetch(ticker)
    news = tavily_search(ticker)

    research_prompt = RESEARCH_PROMPT_TEMPLATE.format(
        ticker=ticker,
        yfinance_json=json.dumps(fin, ensure_ascii=False, indent=2),
        tavily_json=json.dumps(news, ensure_ascii=False, indent=2) if not isinstance(news, str) else news
    )
    research_messages = [
        {"role": "system", "content": "You are an experienced financial research analyst."},
        {"role": "user", "content": research_prompt}
    ]
    research_text, research_usage, research_dur, research_raw = call_llm(research_messages)

    # 2) strategy
    strategy_prompt = STRATEGY_PROMPT_TEMPLATE.format(research_text=research_text)
    strategy_messages = [
        {"role": "system", "content": "You are a seasoned investment strategist."},
        {"role": "user", "content": strategy_prompt}
    ]
    strategy_text, strategy_usage, strategy_dur, strategy_raw = call_llm(strategy_messages)

    # 3) report
    report_prompt = REPORT_PROMPT_TEMPLATE.format(research_text=research_text, strategy_text=strategy_text)
    report_messages = [
        {"role": "system", "content": "You are a professional financial report writer."},
        {"role": "user", "content": report_prompt}
    ]
    report_text, report_usage, report_dur, report_raw = call_llm(report_messages)

    total_time = round(time.time() - t0, 3)

    # aggregate tokens (safe)
    def to_int(v):
        try:
            return int(v) if v is not None else None
        except:
            return None

    input_tokens = sum(filter(None, [to_int(research_usage.get("prompt_tokens")), to_int(strategy_usage.get("prompt_tokens")), to_int(report_usage.get("prompt_tokens"))])) or None
    output_tokens = sum(filter(None, [to_int(research_usage.get("completion_tokens")), to_int(strategy_usage.get("completion_tokens")), to_int(report_usage.get("completion_tokens"))])) or None
    total_tokens = sum(filter(None, [to_int(research_usage.get("total_tokens")), to_int(strategy_usage.get("total_tokens")), to_int(report_usage.get("total_tokens"))])) or None

    token_usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

    intermediate = {
        "research_output": research_text,
        "strategy_output": strategy_text,
        "report_output": report_text
    }

    meta = {
        "agent_durations": {
            "research": research_dur,
            "strategy": strategy_dur,
            "report": report_dur
        },
        "agent_tokens": {
            "research": research_usage,
            "strategy": strategy_usage,
            "report": report_usage
        },
    }

    return {
        "framework": "agno",
        "ticker": ticker,
        "time_seconds": total_time,
        "token_usage": token_usage,
        "intermediate_steps": intermediate,
        "final_result": report_text,
        "meta": meta
    }

# ---------- CLI ----------
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] Agno Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    results = run_agno(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50) 
    print("Analysis complete. Review the final report above.")
    print(f"Analysis: {results}")


