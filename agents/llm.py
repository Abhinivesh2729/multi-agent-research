import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_llm():
    """Get the appropriate LLM based on the LLM_PROVIDER environment variable."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        logger.info(f"Using Ollama LLM: {model} at {base_url}")
        return ChatOllama(model=model, base_url=base_url)
    elif provider == "groq":
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY")
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        logger.info(f"Using Groq LLM: {model}")
        return ChatGroq(api_key=api_key, model=model)
    else:
        logger.warning(f"Unknown LLM provider: {provider}, defaulting to Ollama")
        from langchain_ollama import ChatOllama
        return ChatOllama(model="qwen2.5:3b")
