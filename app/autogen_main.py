# scripts/autogen_script.py
"""
AutoGen implementation for the 3-agent stock analysis workflow.

Install:
  pip install pyautogen openai tavily-python yfinance

Env vars:
  OPENAI_API_KEY
  TAVILY_API_KEY (optional)

Usage:
  from autogen_script import run_autogen
  res = run_autogen("AAPL")
"""

import os
import json
import time
from typing import Dict, Any

import yfinance as yf
from openai import OpenAI
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# ---------- CONFIG -----------

OPENAI_MODEL = "gpt-4o-mini"
client = OpenAI()

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

try:
    from tavily import TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY) if TAVILY_API_KEY else None
except Exception:
    tavily_client = None


# ---------- UTILITIES ----------

def safe_get_usage(resp: Any) -> Dict[str, Any]:
    """Normalize token usage from the OpenAI response."""
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
    """Uniform call to OpenAI chat completions."""
    start = time.perf_counter()
    resp = client.chat.completions.create(
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


# ---------- TOOLS: YF + TAVILY ----------

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


def tavily_search(ticker: str, max_results=5):
    if not tavily_client:
        return "(Tavily unavailable: missing API key)"
    try:
        results = tavily_client.search(query=f"{ticker} stock news", max_results=max_results)
        return results
    except Exception as e:
        return f"(Tavily error: {e})"


# ---------- AUTOGEN AGENTS ----------

def make_research_agent():
    return AssistantAgent(
        name="research_analyst",
        system_message="You are an experienced financial research analyst.",
        llm_config={"model": OPENAI_MODEL}
    )


def make_strategy_agent():
    return AssistantAgent(
        name="investment_strategist",
        system_message="You are a seasoned investment strategist.",
        llm_config={"model": OPENAI_MODEL}
    )


def make_report_agent():
    return AssistantAgent(
        name="report_writer",
        system_message="You are a professional financial report writer.",
        llm_config={"model": OPENAI_MODEL}
    )


def make_supervisor():
    """
    The supervisor coordinates the workflow.
    It does NOT do any reasoning; it only triggers each agent in order.
    """
    return UserProxyAgent(name="supervisor")


# ---------- MAIN WORKFLOW ----------

def run_autogen(ticker: str) -> Dict[str, Any]:
    """
    Full AutoGen workflow with consistent tools + prompts.
    """

    t0 = time.time()

    # Prepare agents
    research_agent = make_research_agent()
    strategy_agent = make_strategy_agent()
    report_agent = make_report_agent()
    supervisor = make_supervisor()

    # 1) Research step -----------------------------------------
    fin = yf_fetch(ticker)
    news = tavily_search(ticker)

    research_prompt = f"""
Gather key news and financial facts for the ticker: {ticker}.

YFinance summary:
{json.dumps(fin, indent=2, ensure_ascii=False)}

Tavily news:
{json.dumps(news, indent=2, ensure_ascii=False) if not isinstance(news,str) else news}

Provide:
1) Top headlines
2) Financial highlights
3) Potential risks
4) Initial observations

Reply as plain text.
"""

    r_text, r_usage, r_dur, r_raw = call_llm([
        {"role": "system", "content": research_agent.system_message},
        {"role": "user",   "content": research_prompt}
    ])

    # 2) Strategy step -----------------------------------------
    strategy_prompt = f"""
Based on this research:

{r_text}

Provide:
- Concise fundamental analysis
- Top 3 risks
- Top 3 opportunities
- Buy/Hold/Sell recommendation with rationale.
"""
    s_text, s_usage, s_dur, s_raw = call_llm([
        {"role": "system", "content": strategy_agent.system_message},
        {"role": "user", "content": strategy_prompt}
    ])

    # 3) Report step -------------------------------------------
    report_prompt = f"""
Write a clean, structured investment report.

Include:
1) Executive summary
2) Research key findings
3) Investment strategy & recommendation
4) Conclusion

Research:
{r_text}

Strategy:
{s_text}
"""

    rep_text, rep_usage, rep_dur, rep_raw = call_llm([
        {"role": "system", "content": report_agent.system_message},
        {"role": "user",   "content": report_prompt}
    ])

    total_time = round(time.time() - t0, 3)

    # Token aggregation
    def safe_int(v):
        try:
            return int(v) if v is not None else None
        except:
            return None

    input_tokens = sum(filter(None, [
        safe_int(r_usage.get("prompt_tokens")),
        safe_int(s_usage.get("prompt_tokens")),
        safe_int(rep_usage.get("prompt_tokens"))
    ])) or None

    output_tokens = sum(filter(None, [
        safe_int(r_usage.get("completion_tokens")),
        safe_int(s_usage.get("completion_tokens")),
        safe_int(rep_usage.get("completion_tokens"))
    ])) or None

    total_tokens = sum(filter(None, [
        safe_int(r_usage.get("total_tokens")),
        safe_int(s_usage.get("total_tokens")),
        safe_int(rep_usage.get("total_tokens"))
    ])) or None

    token_usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens
    }

    return {
        "framework": "autogen",
        "ticker": ticker,
        "time_seconds": total_time,
        "token_usage": token_usage,
        "intermediate_steps": {
            "research_output": r_text,
            "strategy_output": s_text,
            "report_output": rep_text
        },
        "final_result": rep_text,
        "meta": {
            "agent_durations": {
                "research": r_dur,
                "strategy": s_dur,
                "report": rep_dur
            },
            "agent_tokens": {
                "research": r_usage,
                "strategy": s_usage,
                "report": rep_usage
            }
        }
    }


# ---------- CLI ----------
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 AutoGen Stock Analyst[/bold yellow] ")
    print("=" * 50)

    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()  
    results = run_autogen(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Analysis: {results['final_result']}")
    
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