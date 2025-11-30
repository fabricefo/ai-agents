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

def run_langgraph():
    app = create_workflow()
    ticker = input("Enter ticker for which you want recommendations : ")
    initial_state: StockAnalysisState = {"ticker": ticker}
    final_state = app.invoke(initial_state)
    return final_state
# --- Run the workflow ---
if __name__ == "__main__":
    final_state = run_langgraph()
    print("\n--- FINAL RESULTS ---")
    print(f"Ticker: {final_state.get('ticker', 'N/A')}")
    print(f"Analysis: {final_state.get('analysis', 'N/A')}")
    print(f"Recommendation: {final_state.get('recommendation', 'N/A')}")