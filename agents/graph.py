import logging
from langgraph.graph import StateGraph, END
from agents.state import ResearchState
from agents.planner import planner_node
from agents.researcher import researcher_node

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_graph():
    """
    Build the research agent graph.

    Flow:
    - Start with planner_node
    - If error, go to END
    - Otherwise, go to researcher_node
    - researcher_node goes to END
    """
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)

    # Set entry point
    graph.set_entry_point("planner")

    # Add conditional edge from planner
    def should_continue(state: ResearchState) -> str:
        """Route based on whether there's an error."""
        if state.get("error"):
            return "end"
        return "researcher"

    graph.add_conditional_edges(
        "planner",
        should_continue,
        {
            "end": END,
            "researcher": "researcher"
        }
    )

    # Researcher always goes to END
    graph.add_edge("researcher", END)

    return graph.compile()


if __name__ == "__main__":
    # Test the graph with a sample question
    graph = build_graph()

    initial_state = {
        "user_question": "What is the capital of France?",
        "plan": None,
        "search_results": None,
        "final_answer": None,
        "error": None
    }

    print("Testing research graph...")
    print(f"Question: {initial_state['user_question']}")
    print("-" * 50)

    result = graph.invoke(initial_state)

    print("\n=== Results ===")
    print(f"Plan: {result.get('plan', 'N/A')}")
    print(f"\nSearch Results: {result.get('search_results', 'N/A')}")
    print(f"\nFinal Answer: {result.get('final_answer', 'N/A')}")
    if result.get('error'):
        print(f"\nError: {result['error']}")
