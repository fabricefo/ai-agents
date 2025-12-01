# scripts/autogen_script.py
import time
import json
from _common import fetch_financials, fetch_news_tavily, call_llm

import os
from dotenv import load_dotenv
load_dotenv()


FRAMEWORK = "autogen"

# --- Define the LLM for all agents --- 
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
llm = LLM(
    api_key=openai_api_key,
    model="gpt-4o-mini",  
    temperature=0
)

def run_autogen_analysis(ticker: str):
    t0 = time.perf_counter()
    agent_tokens = {}
    agent_durations = {}

    # Research
    fin = fetch_financials(ticker)
    news = fetch_news_tavily(f"{ticker} stock news", max_results=7)
    research_prompt = f"""AutoGen research_analyst:
Fournis une synthèse des news et des données financières pour {ticker}.

Données:
{json.dumps(fin, ensure_ascii=False, indent=2)}

Actualités:
{news}
"""
    messages = [
        {"role": "system", "content": "Tu es research_analyst (AutoGen)."},
        {"role": "user", "content": research_prompt}
    ]
    research_text, usage1, dur1 = call_llm(messages)
    agent_tokens["research"] = usage1
    agent_durations["research"] = dur1

    # Strategy
    strat_prompt = f"""AutoGen investment_strategist:
À partir de l'analyse suivante, fournis une stratégie d'investissement et les risques.
{research_text}
"""
    messages = [
        {"role": "system", "content": "Tu es investment_strategist (AutoGen)."},
        {"role": "user", "content": strat_prompt}
    ]
    strat_text, usage2, dur2 = call_llm(messages)
    agent_tokens["strategy"] = usage2
    agent_durations["strategy"] = dur2

    # Report
    report_prompt = f"""AutoGen report_writer:
Rédige le rapport final structuré.
Research:
{research_text}
Strategy:
{strat_text}
"""
    messages = [
        {"role": "system", "content": "Tu es report_writer (AutoGen)."},
        {"role": "user", "content": report_prompt}
    ]
    report_text, usage3, dur3 = call_llm(messages)
    agent_tokens["report"] = usage3
    agent_durations["report"] = dur3

    total_duration = time.perf_counter() - t0

    def safe_sum(k):
        vals = []
        for a in agent_tokens.values():
            if a and a.get(k) is not None:
                vals.append(int(a.get(k)))
        return sum(vals) if vals else None

    tokens_summary = {
        "input": safe_sum("prompt_tokens"),
        "output": safe_sum("completion_tokens"),
        "total": safe_sum("total_tokens")
    }

    return {
        "result": report_text,
        "tokens": tokens_summary,
        "meta": {
            "framework": FRAMEWORK,
            "duration_seconds": round(total_duration, 3),
            "agent_durations": {k: round(v, 3) for k, v in agent_durations.items()},
            "agent_tokens": agent_tokens
        }
    }




# -------------------------------------------------------
# Main
# -------------------------------------------------------
if __name__ == "__main__":
    # Get user input for the stock ticker
    ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {ticker}[/bold cyan]")
    print("=" * 50)

    final_report = run_autogen_analysis(ticker)
    print("\n[bold cyan]📄 Final report :\n[/bold cyan]")
    print(final_report)
