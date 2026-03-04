import logging
from agents.state import ResearchState
from agents.llm import get_llm
from agents.prompts import RESEARCHER_SYSTEM_PROMPT, FINAL_ANSWER_TEMPLATE

logger = logging.getLogger(__name__)


def _mock_search(query: str) -> str:
    """Mock search function that returns hardcoded results based on query keywords."""
    query_lower = query.lower()

    # 5 hardcoded topic results as specified
    if "france" in query_lower or "paris" in query_lower:
        return "Paris is the capital and largest city of France. It is located in northern France on the Seine River."
    elif "python" in query_lower or "programming" in query_lower:
        return "Python is a high-level, interpreted programming language known for its simplicity and readability."
    elif "ai" in query_lower or "artificial intelligence" in query_lower:
        return "Artificial Intelligence (AI) refers to computer systems designed to perform tasks that typically require human intelligence."
    elif "climate" in query_lower or "weather" in query_lower:
        return "Climate change refers to long-term shifts in global temperatures and weather patterns, primarily caused by human activities."
    elif "space" in query_lower or "mars" in query_lower:
        return "Mars is the fourth planet from the Sun, known as the Red Planet due to its reddish appearance caused by iron oxide on its surface."
    else:
        return f"Search results for '{query}': General information available on this topic."


def researcher_node(state: ResearchState, config: dict = None) -> dict:
    """
    Researcher node that performs search and generates final answer.

    Returns a dict with:
    - {"search_results": "...", "final_answer": "..."} on success
    - {} if error state detected
    """
    status_queue = None
    if config:
        status_queue = config.get("configurable", {}).get("status_queue")

    def emit(event):
        if status_queue is not None:
            status_queue.put(event)

    # Check for error in state
    if state.get("error"):
        logger.info("Error detected in state, skipping researcher")
        return {}

    try:
        # Extract search query from plan
        plan = state.get("plan", "")
        if "Need to search for:" in plan:
            search_query = plan.split("Need to search for:")[-1].strip()
        else:
            search_query = plan

        emit({"type": "status", "step": "researcher_search",
              "message": f"Researcher Agent: Searching for \"{search_query}\"..."})

        # Perform mock search
        search_results = _mock_search(search_query)
        logger.info(f"Search results obtained for: {search_query}")

        emit({"type": "update", "step": "search_done",
              "message": "Researcher Agent: Found relevant information",
              "search_results": search_results})

        # Generate final answer using LLM
        llm = get_llm()
        model_name = getattr(llm, 'model', None) or getattr(llm, 'model_name', 'AI model')
        user_question = state.get("user_question", "")

        prompt = FINAL_ANSWER_TEMPLATE.format(
            user_question=user_question,
            search_results=search_results
        )

        messages = [
            {"role": "system", "content": RESEARCHER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        emit({"type": "status", "step": "researcher_synthesize",
              "message": f"Researcher Agent: Synthesizing answer using {model_name}..."})

        response = llm.invoke(messages)
        final_answer = response.content

        logger.info("Final answer generated")
        emit({"type": "update", "step": "researcher_done",
              "message": "Researcher Agent: Answer generated"})

        return {
            "search_results": search_results,
            "final_answer": final_answer
        }

    except Exception as e:
        logger.error(f"Researcher node error: {e}")
        emit({"type": "error", "step": "researcher_error", "message": f"Researcher failed: {str(e)}"})
        return {"error": f"Researcher failed: {str(e)}"}
