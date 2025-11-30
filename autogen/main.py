import os
from dotenv import load_dotenv

# Handle both relative and absolute imports
try:
    from .agents import create_agents
    from .workflow import create_workflow
except ImportError:
    from agents import create_agents
    from workflow import create_workflow

# --- Load environment variables ---
print("[INFO] Loading environment variables...")
load_dotenv()
print("[INFO] GROQ API key loaded.")
print("[INFO] LLM config initialized (LLaMA 3 70B via Groq).")

# --- Define agents ---
print("[INFO] Setting up agents...")
analyst, researcher, user_proxy = create_agents()
print("[INFO] Agents created successfully.")

# --- Start conversation ---
if __name__ == "__main__":
    print("=" * 50)
    print("📈 AutoGen Stock Analyst")
    print("=" * 50)

    # --- Get stock ticker from user ---
    ticker_symbol = input("Enter the stock ticker symbol (e.g., NVDA, AAPL): ").strip().upper()
    print(f"[INFO] Preparing analysis workflow for {ticker_symbol}...")

    message = (
        f"Analyze {ticker_symbol}'s stock performance for the last quarter. "
        "Gather all relevant financial data and news, then pass it to the Analyst to draft "
        "a report with a buy/sell/hold recommendation."
    )


    # --- Create group chat and manager ---
    manager = create_workflow(researcher, analyst)
    print("[INFO] GroupChat and Manager initialized. Starting the analysis...\n")

    # --- Launch the agent conversation ---
    user_proxy.initiate_chat(
        manager,
        message=message
    )

    print("\n[INFO] Chat completed.")
    print("=" * 50)
    print("✅ Analysis complete. Review the final report above.")
    print("=" * 50)