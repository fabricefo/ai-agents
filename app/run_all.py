# scripts/run_all_analyses.py
import os
import json
from datetime import datetime

from agno_script import run_agno_analysis
from adk_script import run_adk_analysis
from crewai_script import run_crewai_analysis
from autogen_script import run_autogen_analysis
from langgraph_script import run_langgraph_analysis

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

frameworks = [
    ("agno", run_agno_analysis),
    ("adk", run_adk_analysis),
    ("crewai", run_crewai_analysis),
    ("autogen", run_autogen_analysis),
    ("langgraph", run_langgraph_analysis),
]

def export_text(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def export_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def run_all(ticker: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = {"ticker": ticker, "timestamp": timestamp, "frameworks": {}}

    for name, func in frameworks:
        print(f"\n▶ Lancement {name} …")
        res = func(ticker)

        # Enregistre le texte brut
        text_path = os.path.join(OUTPUT_DIR, f"{name}.txt")
        export_text(text_path, res.get("result", ""))

        # Enregistre le détail JSON par framework
        json_path = os.path.join(OUTPUT_DIR, f"{name}.json")
        export_json(json_path, res)

        # Ajoute au résumé central
        summary["frameworks"][name] = {
            "duration_seconds": res.get("meta", {}).get("duration_seconds"),
            "tokens": res.get("tokens"),
            "path_text": text_path,
            "path_json": json_path
        }

        tokens = res.get("tokens")
        if tokens and tokens.get("total") is not None:
            print(f"   🔢 tokens total: {tokens['total']}")
        else:
            print("   🔢 tokens: non disponibles")

        print(f"   ⏱ duration: {res.get('meta', {}).get('duration_seconds')}s")

    # Export summary global
    export_json(os.path.join(OUTPUT_DIR, "summary.json"), summary)
    print("\n✅ All results exported in ./results")

# --------------------------------------------------------------------
# EXECUTION
# --------------------------------------------------------------------

if __name__ == "__main__":
    # Get user input for the stock ticker
    ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {ticker}[/bold cyan]")
    print("=" * 50)

    run_all(ticker)

    print("=" * 50)
    print(f"[bold cyan]End of analysis for: {ticker}[/bold cyan]")
    print("=" * 50)
