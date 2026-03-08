import asyncio
import logging

from agents.llm import get_llm
from agents.prompts import FINAL_ANSWER_TEMPLATE, RESEARCHER_SYSTEM_PROMPT
from agents.state import ResearchState
from mcp.tools.search import handle_search

logger = logging.getLogger(__name__)


def _invoke_mcp_web_search(query: str) -> str:
    """Invoke MCP search handler from sync code and return tool output."""
    try:
        return asyncio.run(handle_search(query))
    except RuntimeError:
        # Fallback for environments where an event loop is already active.
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(handle_search(query))
        finally:
            loop.close()


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

        emit(
            {
                "type": "status",
                "step": "researcher_search",
                "message": f"Researcher Agent: Searching for \"{search_query}\"...",
            }
        )
        emit(
            {
                "type": "status",
                "step": "researcher_mcp_invocation",
                "message": f"Researcher Agent: Invoking MCP tool web_search(query=\"{search_query}\")",
            }
        )

        # Invoke MCP web_search tool handler.
        search_results_raw = _invoke_mcp_web_search(search_query)
        search_results = (
            f"MCP Tool Invocation: web_search(query=\"{search_query}\")\n"
            f"MCP Result: {search_results_raw}"
        )
        logger.info("Search results obtained for: %s", search_query)

        emit(
            {
                "type": "update",
                "step": "search_done",
                "message": "Researcher Agent: Found relevant information",
                "search_results": search_results,
            }
        )

        # Generate final answer using LLM.
        llm = get_llm()
        model_name = getattr(llm, "model", None) or getattr(
            llm, "model_name", "AI model"
        )
        user_question = state.get("user_question", "")

        prompt = FINAL_ANSWER_TEMPLATE.format(
            user_question=user_question,
            search_results=search_results_raw,
        )

        messages = [
            {"role": "system", "content": RESEARCHER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        emit(
            {
                "type": "status",
                "step": "researcher_synthesize",
                "message": f"Researcher Agent: Synthesizing answer using {model_name}...",
            }
        )

        response = llm.invoke(messages)
        final_answer = response.content

        logger.info("Final answer generated")
        emit(
            {
                "type": "update",
                "step": "researcher_done",
                "message": "Researcher Agent: Answer generated",
            }
        )

        return {
            "search_results": search_results,
            "final_answer": final_answer,
        }

    except Exception as e:
        logger.error("Researcher node error: %s", e)
        emit(
            {
                "type": "error",
                "step": "researcher_error",
                "message": f"Researcher failed: {str(e)}",
            }
        )
        return {"error": f"Researcher failed: {str(e)}"}
