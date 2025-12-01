# scripts/adk_script.py
import time
import json
from _common import fetch_financials, fetch_news_tavily, call_llm

FRAMEWORK = "adk"

def run_adk_analysis(ticker: str):
    t0 = time.perf_counter()
    agent_tokens = {}
    agent_durations = {}

    # Research
    fin = fetch_financials(ticker)
    news = fetch_news_tavily(f"{ticker} stock news", max_results=6)
    research_prompt = f"""(ADK) research_analyst: Analyse le ticker {ticker}.
Données financières:
{json.dumps(fin, ensure_ascii=False, indent=2)}

Actualités:
{news}

Return structured analysis."""
    messages = [
        {"role": "system", "content": "Tu es un analyste financier (ADK)."},
        {"role": "user", "content": research_prompt}
    ]
    research_text, usage1, dur1 = call_llm(messages)
    agent_tokens["research"] = usage1
    agent_durations["research"] = dur1

    # Strategy
    strat_prompt = f"""(ADK) investment_strategist: À partir de l'analyse suivante, fournis stratégie et risques.
{research_text}"""
    messages = [
        {"role": "system", "content": "Tu es un investment strategist (ADK)."},
        {"role": "user", "content": strat_prompt}
    ]
    strat_text, usage2, dur2 = call_llm(messages)
    agent_tokens["strategy"] = usage2
    agent_durations["strategy"] = dur2

    # Report
    report_prompt = f"""(ADK) report_writer: Rédige un rapport final, clair et structuré.
Research:
{research_text}

Strategy:
{strat_text}
"""
    messages = [
        {"role": "system", "content": "Tu es un report writer (ADK)."},
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

    final_report = run_adk_analysis(ticker)
    print("\n[bold cyan]📄 Rapport Final :\n[/bold cyan]")
    print(final_report)
