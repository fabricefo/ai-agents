from agno.tasks import Task
from agents import research_analyst,investment_strategist,report_writer

task_research = Task(
    name="stock_research",
    agent=research_analyst,
    instructions="Effectue une analyse complète pour le ticker fourni."
)

task_strategy = Task(
    name="investment_strategy",
    agent=investment_strategist,
    instructions="Analyse les résultats du task stock_research et propose une stratégie."
)

task_report = Task(
    name="report_generation",
    agent=report_writer,
    instructions="Produit une synthèse finale basée sur investment_strategy."
)