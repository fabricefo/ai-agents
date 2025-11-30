import os

def get_llm_config():
    """Get the LLM configuration for AutoGen agents."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    
    return {
        "config_list": [
            {
                "model": "llama-3.3-70b-versatile",
                "api_key": groq_api_key,
                "api_type": "groq"
            }
        ]
    }