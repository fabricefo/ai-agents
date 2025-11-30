from agno.agent import Agent
from agno.tools.tavily import TavilySearch
from agno.models.openai import OpenAIChat
from tools import financial_data_tool
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

llm = OpenAIChat(
    id="gpt-4o-mini",
    api_key=openai_api_key
    )

research_analyst = Agent(
    name="research_analyst",
    description="Analyse le ticker via recherche web (Tavily) et données financières (yfinance).",
    model=llm,
    tools=[
        TavilySearch(max_results=5),
        financial_data_tool
    ],
    instructions="""
    - Utilise Tavily pour obtenir actualités, analyses et informations récentes.
    - Utilise financial_data_tool pour récupérer les données financières du ticker.
    - Retourne une analyse structurée comprenant :
        - Contexte marché
        - Actualités récentes
        - Données financières clés
        - Risques potentiels
    """
)

investment_strategist = Agent(
    name="investment_strategist",
    description="Analyse les documents fournis par l'agent de recherche et donne une stratégie d’investissement.",
    model=llm,
    instructions="""
    Analyse les données transmises et produit :
      - Une analyse fondamentale
      - Risques et volatilité
      - Opportunités
      - Stratégie recommandée (court / moyen / long terme)
    """
)

report_writer = Agent(
    name="report_writer",
    description="Rédige un rapport synthétique clair à destination d'un investisseur.",
    model=llm,
    instructions="""
    Produit une synthèse finale en sections :
      1. Résumé exécutif
      2. Analyse du marché et actualités
      3. Données financières
      4. Recommandation stratégique
      5. Conclusion
    Le ton doit être professionnel, concis et clair.
    """
)