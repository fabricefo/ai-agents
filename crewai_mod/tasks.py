from crewai import Task

# Handle both relative and absolute imports
try:
    from .agents import research_analyst, investment_strategist, report_writer
except ImportError:
    from agents import research_analyst, investment_strategist, report_writer

# --- Define Tasks ---
research_task = Task(
    description=(
        "Research the stock performance of {ticker} for the last quarter. "
        "Use the provided tools to find the financial data and recent news."
    ),
    expected_output="A summary of the stck's performance, key financial metrics, and a list of major news events.",
    agent=research_analyst
)

analysis_task = Task(
    description=(
        "Analyze the research provided by the Research Analyst. "
        "Identify key trends, potential risks, and opportunities. "
        "Conclude with a clear 'buy', 'sell', or 'hold' recommendation. "
    ),
    expected_output="A clear analysis and a buy/sell/hold recommendation with a detailed justification.",
    agent=investment_strategist
)

report_task = Task(
    description=(
        "Write a concise, executive-level report based on the analysis and recommendation. "
        "The report should be professional and easy to understand for a non-specialist audience."
    ),
    expected_output="A final, polished report of the stock analysis and recommendation.",
    agent=report_writer
)