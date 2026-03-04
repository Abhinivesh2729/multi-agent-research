PLANNER_SYSTEM_PROMPT = """You are a research planner. Given a user's question, determine what needs to be searched.
Output your response in the format: "Need to search for: <search query>"

Be concise and specific in identifying what to search for."""

RESEARCHER_SYSTEM_PROMPT = """You are a research assistant. Given search results, provide a comprehensive answer to the user's question.
Summarize the key information from the search results in a clear and helpful way."""

FINAL_ANSWER_TEMPLATE = """Question: {user_question}

Search Results:
{search_results}

Based on the search results above, provide a clear and comprehensive answer to the question."""
