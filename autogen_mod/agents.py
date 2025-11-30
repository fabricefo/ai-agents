from autogen.agentchat import AssistantAgent, UserProxyAgent

# Handle both relative and absolute imports
try:
    from .config import get_llm_config
except ImportError:
    from config import get_llm_config

def create_agents():
    """Create and return all AutoGen agents."""
    llm_config = get_llm_config()
    
    analyst = AssistantAgent(
        name="Analyst",
        llm_config=llm_config,
        system_message="""You are a senior financial analyst.
        Your task is to analyze a stock and draft a report.
        You will get information from the Researcher. Use this information to identify trends, risks, and a clear \"buy\", \"sell\", or \"hold\" recommendation.
        Be sure to explain your reasoning clearly and concisely.
        The final output should be a single, well-structured report.
        Once the report is ready, say 'TERMINATE' to end the conversation.
        """
    )

    researcher = AssistantAgent(
        name="Researcher",
        llm_config=llm_config,
        system_message="""You are an expert stock market researcher.
        Your job is to find and provide data to the Analyst.
        You have the ability to write and execute Python code.
        Use Python and libraries like yfinance and Tavily to get stock data and news.
        Do not provide recommendations yourself, just the raw data.
        """
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy",
        human_input_mode="NEVER",  # type: ignore
        max_consecutive_auto_reply=10,  # type: ignore
        is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),  # type: ignore
        code_execution_config={"work_dir": "coding", "use_docker": False},  # type: ignore
    )
    
    return analyst, researcher, user_proxy