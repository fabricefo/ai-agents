import time
from crewai import Agent, Task, Crew, LLM
import yfinance as yf
from tavily import TavilyClient
from openai import OpenAI

import os
from dotenv import load_dotenv
load_dotenv()

FRAMEWORK = "CrewAI"

# --- Define the LLM for all agents --- 
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
llm = LLM(
    api_key=openai_api_key,
    model="gpt-4o-mini",  
    temperature=0
)

# -------------------------
# OPENAI CLIENT FOR TOKEN STATS
# -------------------------
client = OpenAI(api_key="YOUR_OPENAI_KEY")

def llm_call(model, prompt):
    """
    Wrapper that:
      - calls the LLM
      - returns text + token usage
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "text": response.choices[0].message.content,
        "tokens": response.usage.total_tokens
    }


# -------------------------
# TOOLS: Tavily + YFinance
# -------------------------
tavily = TavilyClient(api_key="YOUR_TAVILY_KEY")

def search_news(ticker):
    return tavily.search(query=f"financial news {ticker}")

def fetch_yf_data(ticker):
    T = yf.Ticker(ticker)
    return {
        "info": T.info,
        "history": T.history(period="6mo").tail(10).to_dict()
    }


# -------------------------
# AGENTS
# -------------------------
research_analyst = Agent(
    name="Research Analyst",
    role="Financial Data Research Agent",
    goal="Gather news and market data for the stock.",
    backstory="Expert in financial markets and data aggregation.",
    llm="gpt-4o-mini",
    verbose=True
)

investment_strategist = Agent(
    name="Investment Strategist",
    role="Financial Strategist",
    goal="Analyze the stock fundamentals and risks.",
    backstory="15 years of experience as a portfolio strategist.",
    llm="gpt-4o-mini",
    verbose=True
)

report_writer = Agent(
    name="Report Writer",
    role="Financial Report Writer",
    goal="Synthesise the final report.",
    backstory="Specialist in financial writing.",
    llm="gpt-4o-mini",
    verbose=True
)


# -------------------------
# TASKS with custom timer + token capture
# -------------------------
def timed_task(task, context):
    """
    Executes a Crew task with:
      - time measurement
      - token measurement
      - returns output + metrics
    """
    start = time.time()
    result = task.execute(context=context)
    end = time.time()

    # Tokens extracted from LLM wrapper
    tokens = result.token_usage if hasattr(result, "token_usage") else None

    return {
        "task_name": task.description[:50],
        "result": result.output,
        "time_seconds": round(end - start, 3),
        "tokens": tokens
    }


task_research = Task(
    description=(
        "Collect Tavily news and YFinance stock data for {{ticker}}. "
        "Return JSON with fields 'news' and 'yfinance'."
    ),
    agent=research_analyst,
    tools=[search_news, fetch_yf_data],
)

task_strategy = Task(
    description=(
        "Analyze the previous task's JSON to evaluate valuation, risks, and opportunities."
    ),
    agent=investment_strategist,
)

task_report = Task(
    description=(
        "Write a final investment report based on the strategist's analysis."
    ),
    agent=report_writer,
)


# -------------------------
# CREW WITHOUT MANAGER
# -------------------------
crew = Crew(
    agents=[research_analyst, investment_strategist, report_writer],
    tasks=[task_research, task_strategy, task_report],
    verbose=True
)


# -------------------------
# MAIN FUNCTION
# -------------------------
def run_crew_with_metrics(ticker: str):
    context = {"ticker": ticker}
    tasks = [task_research, task_strategy, task_report]

    results = []
    total_tokens = 0
    total_time = 0

    for t in tasks:
        r = timed_task(t, context)
        results.append(r)

        if r["tokens"] is not None:
            total_tokens += r["tokens"]

        total_time += r["time_seconds"]

        # Pass result as context to next task
        context = r["result"]

    return {
        "ticker": ticker,
        "task_results": results,
        "total_tokens": total_tokens,
        "total_time_seconds": round(total_time, 3)
    }


# -------------------------------------------------------
# Main
# -------------------------------------------------------
if __name__ == "__main__":
    # Get user input for the stock ticker
    ticker = input("Enter the stock ticker you want to analyze (e.g. NVDA, AMD): ").upper()

    print("=" * 50)
    print(f"[bold cyan]Start analysis for: {ticker}[/bold cyan]")
    print("=" * 50)

    final_report = run_crew_with_metrics(ticker)
    print("\n[bold cyan]📄 Final report :\n[/bold cyan]")
    print(final_report)
