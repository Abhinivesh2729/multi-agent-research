import logging
from agents.state import ResearchState
from agents.llm import get_llm
from agents.prompts import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def planner_node(state: ResearchState, config: dict = None) -> dict:
    """
    Planner node that determines what to search for based on the user's question.

    Returns a dict with either:
    - {"plan": "Need to search for: X"}
    - {"error": "error message"}
    """
    status_queue = None
    if config:
        status_queue = config.get("configurable", {}).get("status_queue")

    def emit(event):
        if status_queue is not None:
            status_queue.put(event)

    try:
        llm = get_llm()
        model_name = getattr(llm, 'model', None) or getattr(llm, 'model_name', 'AI model')
        user_question = state.get("user_question", "")

        emit({"type": "status", "step": "planner_start",
              "message": f"Planner Agent: Analyzing your question using {model_name}..."})

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": user_question}
        ]

        response = llm.invoke(messages)
        plan = response.content

        logger.info(f"Planner generated plan: {plan}")
        emit({"type": "update", "step": "planner_done",
              "message": "Planner Agent: Search plan created", "plan": plan})
        return {"plan": plan}

    except Exception as e:
        logger.error(f"Planner node error: {e}")
        emit({"type": "error", "step": "planner_error", "message": f"Planner failed: {str(e)}"})
        return {"error": f"Planner failed: {str(e)}"}
