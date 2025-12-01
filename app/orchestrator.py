# scripts/orchestrator.py
"""
Orchestrator for multi-framework stock analysis.

Usage:
  python orchestrator.py AAPL

Exports:
  - results_<TICKER>.json
  - summary_<TICKER>.csv
"""

import os
import json
import time
import csv
import argparse

# Import framework scripts
from crewai_main import run_crewai
from langgraph_main import run_langgraph
from autogen_main import run_autogen
from agno_main import run_agno
from adk_main import run_adk

FRAMEWORKS = {
    "CrewAI": run_crewai,
    "LangGraph": run_langgraph,
    "AutoGen": run_autogen,
    "Agno": run_agno,
    "ADK": run_adk
}

def orchestrate(ticker: str):
    ticker = ticker.upper()
    results = []

    for fw_name, fw_func in FRAMEWORKS.items():
        print(f"\n=== Running {fw_name} for {ticker} ===")
        t0 = time.time()
        try:
            fw_result = fw_func(ticker)
        except Exception as e:
            print(f"Error in {fw_name}: {e}")
            fw_result = {
                "framework": fw_name.lower(),
                "ticker": ticker,
                "time_seconds": None,
                "token_usage": None,
                "intermediate_steps": None,
                "final_result": None,
                "meta": {"error": str(e)}
            }
        elapsed = round(time.time() - t0, 3)
        fw_result["elapsed_total_seconds"] = elapsed
        results.append(fw_result)

    # Save JSON
    json_file = f"results_{ticker}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved full results to {json_file}")

    # Save CSV summary
    csv_file = f"summary_{ticker}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = [
            "framework", "elapsed_total_seconds",
            "input_tokens", "output_tokens", "total_tokens",
            "final_result_snippet"
        ]
        writer.writerow(header)
        for r in results:
            tu = r.get("token_usage") or {}
            snippet = (r.get("final_result") or "")[:200].replace("\n", " ")
            row = [
                r.get("framework"),
                r.get("elapsed_total_seconds"),
                tu.get("input_tokens"),
                tu.get("output_tokens"),
                tu.get("total_tokens"),
                snippet
            ]
            writer.writerow(row)
    print(f"Saved CSV summary to {csv_file}")

    return results

# ---------- CLI ----------
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 Orchestrator Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    orchestrate(stock_ticker)
