from langgraph.graph import StateGraph, END

# Handle both relative and absolute imports
try:
    from .state import StockAnalysisState
    from .nodes import research_node, analysis_node, recommendation_node
except ImportError:
    from state import StockAnalysisState
    from nodes import research_node, analysis_node, recommendation_node

def create_workflow():
    """Create and compile the LangGraph workflow."""
    workflow = StateGraph(StockAnalysisState)
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analysis_node)
    workflow.add_node("recommend", recommendation_node)

    workflow.set_entry_point("research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "recommend")
    workflow.add_edge("recommend", END)

    return workflow.compile()