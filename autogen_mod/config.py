import os

def get_llm_config():
    """Get the LLM configuration for AutoGen agents."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    
    return {
        "config_list": [
            {
                "model": "gpt-4o-mini",
                "api_key": openai_api_key,
            }
        ]
    }