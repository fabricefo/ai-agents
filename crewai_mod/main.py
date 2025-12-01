import os
from dotenv import load_dotenv
from crewai import Crew, Process
from rich import print

# Handle both relative and absolute imports
try:
    from .agents import research_analyst, investment_strategist, report_writer
    from .tasks import research_task, analysis_task, report_task
except ImportError:
    from agents import research_analyst, investment_strategist, report_writer
    from tasks import research_task, analysis_task, report_task

load_dotenv()

def run_crewai(stock_ticker: str):
    print(f"[bold blue]Run CrewAI[/bold blue]")

    # Create the crew with the defined agents and tasks
    stock_crew = Crew(
        name="Stock Analysis Crew",
        agents=[research_analyst, investment_strategist, report_writer],
        tasks=[research_task, analysis_task, report_task],
        process=Process.sequential,
        verbose=False,
        max_rpm=5000
    )

    # Use the kickoff method with a dynamic input
    # The {ticket} placeholder in the tasks will be replaced with the user's input.
    result = stock_crew.kickoff(inputs={"ticker": stock_ticker})
    # Récupération des métriques d'usage si disponibles
    usage_metrics = getattr(stock_crew, "usage_metrics", None)
    # On prépare un dict avec les infos utiles
    return {
        "result": result,
        "usage_metrics": usage_metrics
    }



# --- Main execution block ---
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈CrewAI Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    results = run_crewai(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    # Affichage du résultat principal
    analysis = results["result"].get("analysis", "N/A") if isinstance(results["result"], dict) else str(results["result"])
    print(f"Analysis: {analysis}")
    # Affichage des métriques de tokens si disponibles
    usage = results.get("usage_metrics")
    if usage:
        print("\n[bold blue]Token usage metrics:[/bold blue]")
        for attr in ["total_tokens", "prompt_tokens", "completion_tokens", "successful_requests"]:
            value = getattr(usage, attr, None)
            if value is not None:
                print(f"  {attr.replace('_', ' ').capitalize()}: {value}")
    else:
        print("\n[bold blue]Token usage metrics not available.[/bold blue]")
