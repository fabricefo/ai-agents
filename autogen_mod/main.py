import os
from dotenv import load_dotenv
from rich import print

# Handle both relative and absolute imports
try:
    from .agents import create_agents
    from .workflow import create_workflow
except ImportError:
    from agents import create_agents
    from workflow import create_workflow

# --- Load environment variables ---
load_dotenv()

def run_autogen(ticker):
    print(f"[bold blue]Run Autogen[/bold blue]")

    # --- Define agents ---
    analyst, researcher, user_proxy = create_agents()

    message = (
        f"Analyze {ticker}'s stock performance for the last quarter. "
        "Gather all relevant financial data and news, then pass it to the Analyst to draft "
        "a report with a buy/sell/hold recommendation."
    )

    # --- Create group chat and manager ---
    manager = create_workflow(researcher, analyst)

    # --- Launch the agent conversation ---
    results = user_proxy.initiate_chat(
        manager,
        message=message
    )
    return results


# --- Start conversation ---
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈 AutoGen Stock Analyst[/bold yellow] ")
    print("=" * 50)

    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()  
    results = run_autogen(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Ticker: {results.get('ticker', 'N/A')}")
    print(f"Analysis: {results.get('analysis', 'N/A')}")
    print(f"Recommendation: {results.get('recommendation', 'N/A')}")