
from agno.task_pipeline import TaskPipeline
from tasks import task_research,task_strategy,task_report

def run_agno(ticker: str):
    print(f"[bold blue]Run Agno[/bold blue]")
    pipeline = TaskPipeline(
        tasks=[
            task_research,
            task_strategy,
            task_report
        ]
    )
    result = pipeline.run(ticker)
    return result


# --- Main execution block ---
if __name__ == "__main__":
    print("=" * 50)
    print("[bold yellow] 📈CrewAI Stock Analyst[/bold yellow]")
    print("=" * 50)
    
    # Get user input for the stock ticker
    stock_ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()
    results = run_agno(stock_ticker)

    print("=" * 50)
    print("\n[bold yellow]✅ --- FINAL RESULTS ---[/bold yellow]")
    print("=" * 50)
    print("Analysis complete. Review the final report above.")
    print(f"Analysis: {results}")
