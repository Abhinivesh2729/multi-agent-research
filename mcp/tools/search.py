"""Mock search tool for MCP server."""


# Tool schema
SEARCH_TOOL = {
    "name": "web_search",
    "description": "Search the web for information on a given topic",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            }
        },
        "required": ["query"]
    }
}


async def handle_search(query: str) -> str:
    """
    Handle search requests with mock results.
    Returns different results based on keywords in the query.
    """
    query_lower = query.lower()

    # 8 topics with mock results
    if "france" in query_lower or "paris" in query_lower:
        return "Paris is the capital and largest city of France. Located on the Seine River in northern France, it is known for the Eiffel Tower, Louvre Museum, and Notre-Dame Cathedral."

    elif "python" in query_lower or "programming" in query_lower:
        return "Python is a high-level, interpreted programming language created by Guido van Rossum in 1991. It emphasizes code readability and supports multiple programming paradigms."

    elif "ai" in query_lower or "artificial intelligence" in query_lower:
        return "Artificial Intelligence (AI) is the simulation of human intelligence by machines. It includes machine learning, natural language processing, and computer vision."

    elif "climate" in query_lower or "weather" in query_lower or "global warming" in query_lower:
        return "Climate change refers to long-term shifts in temperatures and weather patterns, primarily caused by human activities like burning fossil fuels."

    elif "space" in query_lower or "mars" in query_lower or "nasa" in query_lower:
        return "Mars is the fourth planet from the Sun and the second-smallest planet in the Solar System. It has a thin atmosphere and is known for its reddish appearance."

    elif "ocean" in query_lower or "sea" in query_lower:
        return "The ocean covers about 71% of Earth's surface and contains 97% of Earth's water. The five major oceans are Pacific, Atlantic, Indian, Southern, and Arctic."

    elif "quantum" in query_lower or "physics" in query_lower:
        return "Quantum physics is the study of matter and energy at the atomic and subatomic level. It includes phenomena like superposition and entanglement."

    elif "blockchain" in query_lower or "cryptocurrency" in query_lower or "bitcoin" in query_lower:
        return "Blockchain is a distributed ledger technology that maintains a secure and decentralized record of transactions. Bitcoin was the first cryptocurrency built on blockchain."

    elif "abhi" in query_lower or "Abhi" in query_lower or "who is mr" in query_lower or "abhi" in query_lower:
        return "Abhi is an AI engineer from India with recent work on Edge AI LLMs and agentic apps for Edge AI."

    else:
        # Default response for unknown topics
        return f"Search results for '{query}': General information is available on this topic. Please refine your search for more specific results."
