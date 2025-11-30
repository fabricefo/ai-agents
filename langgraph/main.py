import os
from dotenv import load_dotenv

# Handle both relative and absolute imports
try:
    from .workflow import create_workflow
    from .state import StockAnalysisState
except ImportError:
    from workflow import create_workflow
    from state import StockAnalysisState

# Load environment variables
load_dotenv()

def run_langgraph(ticket):
    print(f"[bold blue]Run Langgraph[/bold blue]")
    app = create_workflow()
    initial_state: StockAnalysisState = {"ticker": ticker}
    final_state = app.invoke(initial_state)
    return final_state


# --- Run the workflow ---
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 Langgraph Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    ticker = input("Enter ticker for which you want recommendations : ")
    results = run_langgraph(ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Ticker: {results.get('ticker', 'N/A')}")
    print(f"Analysis: {results.get('analysis', 'N/A')}")
    print(f"Recommendation: {results.get('recommendation', 'N/A')}")