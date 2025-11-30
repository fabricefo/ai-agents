
from crewai_mod.main import run_crewai
from langgraph_mod.main import run_langgraph
from autogen_mod.main import run_autogen
from rich import print
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Main execution block ---
if __name__ == "__main__":
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {stock_ticker}[/bold cyan]")
    print("=" * 50)
    
    crewai_results = run_crewai(stock_ticker)
    autogen_results = run_autogen(stock_ticker)
    langgraph_results = run_langgraph(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- CREWAI FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("CrewAI Analysis complete. Review the final report above.")
    print(f"Analysis: {crewai_results.get('analysis', 'N/A')[:50]}")
    with open("results_CrewAI.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {crewai_results.get('analysis', 'N/A')}")


    print("=" * 50)
    print("\n[bold yellow]✅ --- AUTOGEN FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Analysis: {autogen_results}")
    with open("results_Autogen.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {autogen_results}")

    print("=" * 50)
    print("\n[bold yellow]✅ --- LANGGRAPH FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Analysis: {langgraph_results}")
    with open("results_Langgraph.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {langgraph_results}")
