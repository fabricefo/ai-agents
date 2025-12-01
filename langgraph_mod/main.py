import os
from dotenv import load_dotenv
from rich import print

# Handle both relative and absolute imports
try:
    from .workflow import create_workflow
    from .state import StockAnalysisState
except ImportError:
    from workflow import create_workflow
    from state import StockAnalysisState

# Load environment variables
load_dotenv()

def run_langgraph(ticker: str):
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
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    langgraph_results = run_langgraph(stock_ticker)

    langgraph_analysis = langgraph_results.get('analysis', 'N/A')
    langgraph_recommendation = langgraph_results.get('recommendation', 'N/A')

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Analysis: {langgraph_analysis}")
    print(f"Recommendation: {langgraph_recommendation}")