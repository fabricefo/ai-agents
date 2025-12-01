# scripts/langgraph_script.py
"""
LangGraph implementation for the 3-agent stock analysis workflow.

Pre-req:
  pip install openai tavily-python yfinance langgraph

Environment:
  OPENAI_API_KEY, TAVILY_API_KEY (optional: script will still run if Tavily missing)

Usage:
  from langgraph_script import run_langgraph
  res = run_langgraph("AAPL")
"""

import os
import time
import json
from typing import Any, Dict

# LangGraph imports
from langgraph.graph import StateGraph, END

# External services
import yfinance as yf
from openai import OpenAI

# Lazy import Tavily (optional)
try:
    from tavily import TavilyClient
except Exception:
    TavilyClient = None

# ---------- CONFIG ----------
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_CLIENT = OpenAI()  # reads OPENAI_API_KEY from environment

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")
TAVILY_CLIENT = None
if TavilyClient and TAVILY_API_KEY:
    try:
        TAVILY_CLIENT = TavilyClient(api_key=TAVILY_API_KEY)
    except Exception:
        TAVILY_CLIENT = None

# ---------- UTILITIES ----------

def safe_get_usage(resp: Any) -> Dict[str, Any]:
    """
    Normalize response.usage into a dict with prompt_tokens, completion_tokens, total_tokens.
    Works across SDK variants.
    """
    usage = {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    try:
        u = getattr(resp, "usage", None) or (resp.get("usage") if isinstance(resp, dict) else None)
        if u is None:
            return usage
        # u might be an object or dict
        try:
            usage["prompt_tokens"] = int(u.prompt_tokens) if hasattr(u, "prompt_tokens") else int(u.get("prompt_tokens"))
        except Exception:
            usage["prompt_tokens"] = None
        try:
            usage["completion_tokens"] = int(u.completion_tokens) if hasattr(u, "completion_tokens") else int(u.get("completion_tokens"))
        except Exception:
            usage["completion_tokens"] = None
        try:
            usage["total_tokens"] = int(u.total_tokens) if hasattr(u, "total_tokens") else int(u.get("total_tokens"))
        except Exception:
            # fallback: sum if available
            pt = usage["prompt_tokens"] or 0
            ct = usage["completion_tokens"] or 0
            usage["total_tokens"] = pt + ct if (pt or ct) else None
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

    # Extract text
    try:
        text = resp.choices[0].message.content
    except Exception:
        # fallback to string representation
        try:
            text = str(resp)
        except Exception:
            text = ""

    usage = safe_get_usage(resp)
    return text, usage, round(duration, 3), resp

# ---------- Tools: YFinance & Tavily ----------

def yf_fetch(ticker: str) -> Dict[str, Any]:
    """Return a compact dict with key financial fields (best-effort)."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        # keep only a few fields to avoid huge prompts
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
    """Return Tavily hits or a message if not available."""
    if TAVILY_CLIENT is None:
        return f"(Tavily unavailable; set TAVILY_API_KEY to enable news search)"
    try:
        # SDKs vary; use search(query=...) style
        hits = TAVILY_CLIENT.search(query=f"{ticker} stock news", max_results=max_results)
        return hits
    except Exception as e:
        return f"(Tavily error: {e})"

# ---------- LangGraph Node implementations ----------

class StockState(dict):
    """State object (dict-like) used by the graph nodes."""
    pass

def research_node(state: StockState):
    ticker = state.get("ticker")
    if not ticker:
        return {"research": "No ticker provided."}

    # Prepare inputs
    fin = yf_fetch(ticker)
    news = tavily_search(ticker)

    # Build prompt (concise, consistent with other frameworks)
    prompt = f"""
You are research_analyst.
Gather key news and financial facts for the ticker: {ticker}.

YFinance summary (JSON):
{json.dumps(fin, ensure_ascii=False, indent=2)}

Tavily news (raw):
{json.dumps(news, ensure_ascii=False, indent=2) if not isinstance(news, str) else news}

Output a structured analysis with sections:
1) Top headlines (short)
2) Financial highlights (bullet)
3) Potential risks (bullet)
4) Initial observations (short)
Respond as plain text.
"""
    messages = [
        {"role": "system", "content": "You are an experienced financial research analyst."},
        {"role": "user", "content": prompt}
    ]
    text, usage, duration, raw = call_llm(messages)
    return {
        "research": text,
        "research_usage": usage,
        "research_duration": duration,
        "research_raw": {"yfinance": fin, "tavily": news}
    }

def strategy_node(state: StockState):
    research_text = state.get("research", "")
    prompt = f"""
You are investment_strategist.
Based on the research below, provide:
- A concise fundamental analysis (1-2 paragraphs)
- Top 3 risks
- Top 3 opportunities
- A recommendation: Buy / Hold / Sell (with rationale)
Research (start):
{research_text}
Research (end)
"""
    messages = [
        {"role": "system", "content": "You are a seasoned investment strategist."},
        {"role": "user", "content": prompt}
    ]
    text, usage, duration, raw = call_llm(messages)
    return {
        "strategy": text,
        "strategy_usage": usage,
        "strategy_duration": duration
    }

def report_node(state: StockState):
    research_text = state.get("research", "")
    strategy_text = state.get("strategy", "")
    prompt = f"""
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
    messages = [
        {"role": "system", "content": "You are a professional financial report writer."},
        {"role": "user", "content": prompt}
    ]
    text, usage, duration, raw = call_llm(messages)
    return {
        "report": text,
        "report_usage": usage,
        "report_duration": duration
    }

# ---------- Build Graph ----------

graph = StateGraph(StockState)
graph.add_node("research", research_node)
graph.add_node("strategy", strategy_node)
graph.add_node("report", report_node)
graph.set_entry_point("research")
graph.add_edge("research", "strategy")
graph.add_edge("strategy", "report")
graph.add_edge("report", END)

app = graph.compile()

# ---------- Runner function (exported) ----------

def run_langgraph(ticker: str) -> Dict[str, Any]:
    """
    Execute the LangGraph workflow and return the unified result format.
    """
    t0 = time.time()
    initial_state = StockState({"ticker": ticker})
    # invoke the graph
    result_state = app.invoke(initial_state)  # returns final state dict

    total_time = round(time.time() - t0, 3)

    # Extract node outputs & usage/durations
    research_section = result_state.get("research") or result_state.get("research", "")
    strategy_section = result_state.get("strategy") or result_state.get("strategy", "")
    report_section = result_state.get("report") or result_state.get("report", "")

    # In our node returns we included usage/duration fields inside the state,
    # but depending on StateGraph internals they may be nested. We try to extract safely.
    def extract_field(state, key_base):
        """Try multiple patterns to extract usage/duration."""
        # direct keys
        usage = None
        duration = None
        # check for e.g. "research_usage" etc in state
        u_key = f"{key_base}_usage"
        d_key = f"{key_base}_duration"
        if u_key in result_state:
            usage = result_state.get(u_key)
        if d_key in result_state:
            duration = result_state.get(d_key)
        # otherwise maybe nested in a dict under key_base + "_raw" etc.
        # try fallback to None
        return usage, duration

    # Attempt extraction (best effort)
    research_usage = result_state.get("research_usage") if "research_usage" in result_state else None
    strategy_usage = result_state.get("strategy_usage") if "strategy_usage" in result_state else None
    report_usage = result_state.get("report_usage") if "report_usage" in result_state else None

    research_duration = result_state.get("research_duration") if "research_duration" in result_state else None
    strategy_duration = result_state.get("strategy_duration") if "strategy_duration" in result_state else None
    report_duration = result_state.get("report_duration") if "report_duration" in result_state else None

    # Fallback: if usage not present on final state, attempt to re-run small token-only estimations (avoid by design)
    # Aggregate token counts
    def safe_int(v):
        try:
            return int(v) if v is not None else None
        except Exception:
            return None

    input_tokens = sum([safe_int(x.get("prompt_tokens")) for x in [research_usage, strategy_usage, report_usage] if x]) or None
    output_tokens = sum([safe_int(x.get("completion_tokens")) for x in [research_usage, strategy_usage, report_usage] if x]) or None
    total_tokens = sum([safe_int(x.get("total_tokens")) for x in [research_usage, strategy_usage, report_usage] if x]) or None

    token_usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

    # Build intermediate steps
    intermediate = {
        "research_output": research_section,
        "strategy_output": strategy_section,
        "report_output": report_section
    }

    # final result is the report text
    final_report = report_section if report_section else ""

    # meta: include agent durations & per-agent token objects (raw)
    agent_durations = {
        "research": research_duration,
        "strategy": strategy_duration,
        "report": report_duration
    }
    agent_tokens = {
        "research": research_usage,
        "strategy": strategy_usage,
        "report": report_usage
    }

    return {
        "framework": "langgraph",
        "ticker": ticker,
        "time_seconds": total_time,
        "token_usage": token_usage,
        "intermediate_steps": intermediate,
        "final_result": final_report,
        "meta": {
            "agent_durations": agent_durations,
            "agent_tokens": agent_tokens
        }
    }

# ---------- Quick CLI ----------
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 Langgraph Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter ticker for which you want recommendations : ")
    results = run_langgraph(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Ticker: {results.get('ticker', 'N/A')}")
    print(f"Analysis: {results.get('final_result', 'N/A')}")    
    print(f"Recommendation: {results.get('meta', {}).get('agent_tokens', {}).get('report', {}).get('recommendation', 'N/A')}")
    
    # Affichage des métriques de tokens si disponibles
    usage = results.get("token_usage")
    if usage:
        print("\n[bold blue]Token usage metrics:[/bold blue]")
        for attr in ["total_tokens", "input_tokens", "output_tokens"]:
            value = usage.get(attr)
            if value is not None:
                print(f"  {attr.replace('_', ' ').capitalize()}: {value}")
    else:
        print("\n[bold blue]Token usage metrics not available.[/bold blue]")