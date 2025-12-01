
from crewai_mod.main import run_crewai
from langgraph_mod.main import run_langgraph
from autogen_mod.main import run_autogen
from rich import print
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

openai_client = OpenAI(api_key=openai_api_key)

def llm_call(prompt: str) -> str:
    """Appelle l'API OpenAI et retourne la réponse textuelle."""
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# --- Main execution block ---
if __name__ == "__main__":
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {stock_ticker}[/bold cyan]")
    print("=" * 50)

    # ======================================================================
    # Run CrewAI
    # ======================================================================
    crewai_results = run_crewai(stock_ticker)
    print("=" * 50)
    print("\n[bold yellow]✅ --- CREWAI FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("CrewAI Analysis complete. Review the final report above.")
    crewai_analysis = crewai_results.get("analysis", "N/A") if isinstance(crewai_results, dict) else str(crewai_results)
    print(f"Analysis: {crewai_analysis}")

    with open("outputs/results_CrewAI.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {crewai_analysis}")

    # ======================================================================
    # Run Autogen
    # ======================================================================
    # autogen_results = run_autogen(stock_ticker)
    # print("=" * 50)
    # print("\n[bold yellow]✅ --- AUTOGEN FINAL RESULTS ---[/bold yellow]")
    # print("=" * 50)
    # print(f"Analysis: {autogen_results}")
    # with open("outputs/results_Autogen.md", "x", encoding="utf-8") as f:
    #     f.write(f"Analysis: {autogen_results}")

    # ======================================================================
    # Run LangGraph
    # ======================================================================
    langgraph_results = run_langgraph(stock_ticker)
    langgraph_analysis = langgraph_results.get('analysis', 'N/A')
    langgraph_recommendation = langgraph_results.get('recommendation', 'N/A')
    
    print("=" * 50)
    print("\n[bold yellow]✅ --- LANGGRAPH FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print(f"Analysis: {langgraph_analysis}")
    print(f"Recommendation: {langgraph_recommendation}")
    with open("outputs/results_Langgraph.md", "x", encoding="utf-8") as f:
        f.write(f"Analysis: {langgraph_analysis}")
        f.write(f"Recommendation: {langgraph_recommendation}")

    print("=" * 50)
    print("\n[bold green]All analyses complete. Results saved in outputs/ folder.[/bold green]")
    print("=" * 50)

    # Call LLM to summarize results
    summary_prompt = f"Summarize and compare the following stock analyses for {stock_ticker}:\n\nCrewAI Analysis:\n{crewai_analysis}\n\nLangGraph Analysis:\n{langgraph_analysis}\n\nProvide a concise summary highlighting key insights from both analyses."
    summary = llm_call(summary_prompt)
    print("\n[bold magenta]📝 --- SUMMARY OF ALL ANALYSES ---[/bold magenta]")
    print(summary)
    with open("outputs/summary_of_analyses.md", "x", encoding="utf-8") as f:
        f.write(summary)
    print("=" * 50)
    print("\n[bold green]Summary saved to outputs/summary_of_analyses.md[/bold green]")
    print("=" * 50)




