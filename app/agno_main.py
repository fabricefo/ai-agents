# scripts/agno_script.py
import time
import json
from _common import fetch_financials, fetch_news_tavily, call_llm

FRAMEWORK = "agno"

def run_agno_analysis(ticker: str):
    t0 = time.perf_counter()
    agent_tokens = {}
    agent_durations = {}

    # 1) Research agent: Tavily + yfinance
    fin = fetch_financials(ticker)
    news = fetch_news_tavily(f"{ticker} stock news", max_results=5)
    research_prompt = f"""Vous êtes research_analyst (AGNO).
Fournissez une analyse structurée pour le ticker {ticker}.

Données financières (yfinance):
{json.dumps(fin, ensure_ascii=False, indent=2)}

Actualités (Tavily):
{news}

Sortie attendue : 
1) Actualités importantes
2) Données financières clés
3) Points forts
4) Risques
"""
    messages = [
        {"role": "system", "content": "Tu es un analyste financier expérimenté (AGNO)."},
        {"role": "user", "content": research_prompt}
    ]
    research_text, usage1, dur1 = call_llm(messages)
    agent_tokens["research"] = usage1
    agent_durations["research"] = dur1

    # 2) Investment strategist
    strat_prompt = f"""Vous êtes investment_strategist (AGNO).
À partir de l'analyse suivante, produisez :
- Analyse fondamentale synthétique
- Opportunités
- Risques
- Stratégie recommandée (CT/MT/LT)

Analyse fournie:
{research_text}
"""
    messages = [
        {"role": "system", "content": "Tu es un investment strategist expérimenté (AGNO)."},
        {"role": "user", "content": strat_prompt}
    ]
    strat_text, usage2, dur2 = call_llm(messages)
    agent_tokens["strategy"] = usage2
    agent_durations["strategy"] = dur2

    # 3) Report writer
    report_prompt = f"""Vous êtes report_writer (AGNO).
Rédigez un rapport final structuré pour un investisseur en incluant :
1. Résumé exécutif
2. Points clés des actualités
3. Données financières essentielles
4. Recommandation stratégique
5. Conclusion

Inputs :
Research:
{research_text}

Strategy:
{strat_text}
"""
    messages = [
        {"role": "system", "content": "Tu es un rédacteur financier professionnel (AGNO)."},
        {"role": "user", "content": report_prompt}
    ]
    report_text, usage3, dur3 = call_llm(messages)
    agent_tokens["report"] = usage3
    agent_durations["report"] = dur3

    total_duration = time.perf_counter() - t0

    # Sum tokens across agents if available
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

    final_report = run_agno_analysis(ticker)
    print("\n[bold cyan]📄 Final report :\n[/bold cyan]")
    print(final_report)

