from autogen import GroupChat, GroupChatManager

# Handle both relative and absolute imports
try:
    from .config import get_llm_config
except ImportError:
    from config import get_llm_config

def create_workflow(researcher, analyst):
    """Create the AutoGen workflow with GroupChat."""
    llm_config = get_llm_config()
    
    groupchat = GroupChat(
        agents=[researcher, analyst],
        messages=[],
        max_round=3,
        speaker_selection_method="round_robin"
    )
    
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )
    
    return manager