from typing import Optional, TypedDict


class ResearchState(TypedDict, total=False):
    """State for the research agent graph."""
    user_question: str  # required
    plan: Optional[str]
    search_results: Optional[str]
    final_answer: Optional[str]
    error: Optional[str]
