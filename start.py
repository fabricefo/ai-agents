
from crewai_mod.main import run_crewai
from langgraph_mod.main import run_langgraph
from autogen_mod.main import run_autogen
from rich import print
import os
from dotenv import load_dotenv
import csv

# Load environment variables
load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {stock_ticker}[/bold cyan]")
    print("=" * 50)

    results = []    
    crewai_results = run_crewai(stock_ticker)
    autogen_results = run_autogen(stock_ticker)
    langgraph_results = run_langgraph(stock_ticker)

    # ======================================================================
    # Run CrewAI
    # ======================================================================
    print("=" * 50)
    print("\n[bold yellow]✅ --- CREWAI FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("CrewAI Analysis complete. Review the final report above.")
    print(f"Analysis: {crewai_results.get('analysis', 'N/A')[:50]}")
    analysis = crewai_results["result"].get("analysis", "N/A") if isinstance(results["result"], dict) else str(results["result"])
    print(f"Analysis: {analysis}")
    # Affichage des métriques de tokens si disponibles
    usage = crewai_results.get("usage_metrics")
    if usage:
        print("\n[bold blue]Token usage metrics:[/bold blue]")
        for attr in ["total_tokens", "prompt_tokens", "completion_tokens", "successful_requests"]:
            value = getattr(usage, attr, None)
            if value is not None:
                print(f"  {attr.replace('_', ' ').capitalize()}: {value}")
    else:
        print("\n[bold blue]Token usage metrics not available.[/bold blue]")

    with open("results_CrewAI.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {crewai_results.get('analysis', 'N/A')}")

    # ======================================================================
    # Run Autogen
    # ======================================================================
    print("=" * 50)
    print("\n[bold yellow]✅ --- AUTOGEN FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Analysis: {autogen_results}")
    with open("results_Autogen.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {autogen_results}")

    # ======================================================================
    # Run LangGraph
    # ======================================================================
    print("=" * 50)
    print("\n[bold yellow]✅ --- LANGGRAPH FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Analysis: {langgraph_results}")
    with open("results_Langgraph.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {langgraph_results}")



