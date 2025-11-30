import os
from crewai import Agent, LLM

# Handle both relative and absolute imports
try:
    from .tools import tavily_search, yfinance_data
except ImportError:
    from tools import tavily_search, yfinance_data

# --- Define the LLM for all agents --- 
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
llm = LLM(
    api_key=openai_api_key,
    model="gpt-4o-mini",  
    temperature=0
)

# --- Define Agents ---
research_analyst = Agent(
    role='Senior Financial Research Analyst',
    goal='Gather and summarize financal data and news on a company.',
    backstory=(
        "A seasoned analyst who excels at finding the most relevent financial information "
        "and market trends from various sources."
    ),
    tools=[tavily_search, yfinance_data], # type: ignore
    llm=llm,
    verbose=True
)

investment_strategist = Agent(
    role='Chief Investment Strategist',
    goal='Analyze research to formulate an investment recommendation.',
    backstory=(
        "An expert stratergist with a deep understanding of market dynamics, able to "
        "synthesize complex data into a clear 'buy', 'sell', or 'hold' recommendation."
    ),
    llm=llm,
    verbose=True
)

report_writer = Agent(
    role='Executive Report Writer',
    goal='Draft a professional, executive-level report.',
    backstory=(
        "A professional communicator who turns complex analysis into a consice, easy-to-read "
        "report for high-level decision-makers."
    ),
    llm=llm,
    verbose=True
)