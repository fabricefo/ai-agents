import os
from crewai import Agent, LLM

# Handle both relative and absolute imports
try:
    from .tools import tavily_search, yfinance_data
except ImportError:
    from tools import tavily_search, yfinance_data

# --- Define the LLM for all agents --- 
openai_llm = LLM(
    api_key=os.getenv("OPEN_API_KEY"),
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
    llm=openai_llm,
    verbose=True
)

investment_stratergist = Agent(
    role='Chief Investment Stratergist',
    goal='Analyze research to formulate an investment recommendation.',
    backstory=(
        "An expert stratergist with a deep understanding of market dynamics, able to "
        "synthesize complex data into a clear 'buy', 'sell', or 'hold' recommendation."
    ),
    llm=openai_llm,
    verbose=True
)

report_writer = Agent(
    role='Executive Report Writer',
    goal='Draft a professional, executive-level report.',
    backstory=(
        "A professional communicator who turns complex analysis into a consice, easy-to-read "
        "report for high-level decision-makers."
    ),
    llm=openai_llm,
    verbose=True
)