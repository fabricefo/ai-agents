

from crewai.main import run_crewai
from langgraph.main import run_autogen
from autogen.main import run_langgraph

# --- Main execution block ---
if __name__ == "__main__":
    crewai_results = run_crewai()
    # autogen_results = run_autogen()
    # langgraph_results = run_langgraph()