

from crewai.main import run_crewai
from langgraph.main import run_autogen
from autogen.main import run_langgraph

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
    print(f"Ticker: {crewai_results.get('ticker', 'N/A')}")
    print(f"Analysis: {crewai_results.get('analysis', 'N/A')}")
    print(f"Recommendation: {crewai_results.get('recommendation', 'N/A')}")

    print("=" * 50)
    print("\n[bold yellow]✅ --- AUTOGEN FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Ticker: {autogen_results.get('ticker', 'N/A')}")
    print(f"Analysis: {autogen_results.get('analysis', 'N/A')}")
    print(f"Recommendation: {autogen_results.get('recommendation', 'N/A')}")

    print("=" * 50)
    print("\n[bold yellow]✅ --- LANGGRAPH FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Ticker: {langgraph_results.get('ticker', 'N/A')}")
    print(f"Analysis: {langgraph_results.get('analysis', 'N/A')}")
    print(f"Recommendation: {langgraph_results.get('recommendation', 'N/A')}")