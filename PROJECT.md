# PROJECT.md — Assignment 1: Multi-Agent Research Assistant

## EXECUTION INSTRUCTIONS FOR CLAUDE CODE
Read this entire file before writing any code.
Build everything in the order listed in the BUILD ORDER section.
After building, run all tests listed in the TEST SUITE section.
Do not ask clarifying questions. Make decisions based on this spec.
If something is ambiguous, choose the simpler option.

---

## PROJECT OVERVIEW
Multi-agent research assistant using LangGraph.
A Planner agent + Research agent answer user questions.
Exposed via Django REST API.
Displayed in Streamlit chat UI.
MCP server provides mock search tool.

---

## TECH STACK (DO NOT DEVIATE)
- Python 3.11
- LLM: Ollama with qwen2.5:3b via langchain-ollama
- Agents: LangChain + LangGraph
- Backend: Django 4.2 + djangorestframework
- Frontend: Streamlit
- Database: PostgreSQL via psycopg2-binary + dj-database-url
- MCP: mcp Python package
- Env vars: python-dotenv

---

## FOLDER STRUCTURE TO CREATE
assignment-1/
├── PROJECT.md
├── CLAUDE.md
├── README.md
├── .env.example
├── .gitignore
├── requirements.txt
├── Procfile
├── agents/
│   ├── init.py
│   ├── llm.py
│   ├── state.py
│   ├── prompts.py
│   ├── planner.py
│   ├── researcher.py
│   └── graph.py
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── init.py
│   │   ├── settings/
│   │   │   ├── init.py
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       └── conversations/
│           ├── init.py
│           ├── models.py
│           ├── views.py
│           ├── serializers.py
│           ├── urls.py
│           └── tests.py
├── mcp/
│   ├── init.py
│   ├── server.py
│   └── tools/
│       ├── init.py
│       └── search.py
├── ui/
│   ├── app.py
│   └── .streamlit/
│       └── config.toml
└── tests/
├── init.py
├── test_agents.py
├── test_api.py
└── test_mcp.py

---

## ENVIRONMENT VARIABLES
Create .env.example with these keys (no values):
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
GROQ_API_KEY=
GROQ_MODEL=llama-3.3-70b-versatile
DJANGO_SECRET_KEY=
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/research_assistant
REDIS_URL=redis://localhost:6379/0
DJANGO_API_URL=http://localhost:8000

---

## FILE SPECIFICATIONS

### agents/state.py
TypedDict called ResearchState with these optional fields:
- user_question: str (required)
- plan: Optional[str]
- search_results: Optional[str]  
- final_answer: Optional[str]
- error: Optional[str]

### agents/llm.py
Function get_llm() that:
- Reads LLM_PROVIDER env var (default "ollama")
- Returns ChatOllama if "ollama", ChatGroq if "groq"
- Logs which provider is being used

### agents/prompts.py
Three constants:
- PLANNER_SYSTEM_PROMPT: tells LLM to output "Need to search for: X"
- RESEARCHER_SYSTEM_PROMPT: tells LLM to summarize search results
- FINAL_ANSWER_TEMPLATE: string with {user_question} and {search_results} placeholders

### agents/planner.py
Function planner_node(state: ResearchState) -> dict:
- Calls LLM with PLANNER_SYSTEM_PROMPT
- Returns {"plan": "Need to search for: X"}
- Returns {"error": "..."} on failure

### agents/researcher.py
Function researcher_node(state: ResearchState) -> dict:
- Checks for error in state, returns {} if found
- Extracts search query from plan
- Calls _mock_search() with 5 hardcoded topic results
- Calls LLM to generate final answer using FINAL_ANSWER_TEMPLATE
- Returns {"search_results": "...", "final_answer": "..."}

### agents/graph.py
Function build_graph() that:
- Creates StateGraph(ResearchState)
- Adds planner_node and researcher_node
- Sets planner as entry point
- Adds conditional edge: if error -> END, else -> researcher
- Returns compiled graph

Runnable as __main__ with test question "What is the capital of France?"

### backend/config/settings/base.py
Standard Django settings plus:
- REST_FRAMEWORK with default JSON renderer
- INSTALLED_APPS includes rest_framework and conversations app
- DATABASES reads from DATABASE_URL env var
- LOGGING config that logs to console at INFO level
- sys.path insert for project root so agents/ can be imported

### backend/apps/conversations/models.py
Model Conversation:
- id: UUIDField primary key
- question: TextField
- plan: TextField blank=True
- search_results: TextField blank=True
- answer: TextField
- created_at: DateTimeField auto_now_add

### backend/apps/conversations/views.py
Two views:
1. ask_question POST /api/ask/
   - Validates question not empty
   - Calls build_graph().invoke()
   - Saves Conversation to DB
   - Returns {id, question, plan, search_results, answer, error}
   
2. list_conversations GET /api/conversations/
   - Returns last 20 conversations

### mcp/tools/search.py
- SEARCH_TOOL: Tool object with name, description, inputSchema
- handle_search(query: str) -> str: returns mock results for 8 topics

### mcp/server.py
- MCP Server named "research-mcp"
- Registers SEARCH_TOOL
- Handles call_tool for web_search
- Runnable as __main__ with asyncio + stdio_server

### ui/app.py
Streamlit app that:
- Reads DJANGO_API_URL from env
- Shows chat history in session_state
- Input via st.chat_input
- POSTs to /api/ask/
- Shows answer prominently
- Shows plan + search_results in st.expander("Agent Steps")
- Shows error if API is down
- 60 second timeout on requests

---

## BUILD ORDER
Build in this exact sequence (each step depends on previous):

1. Create requirements.txt
2. Create .env.example and .gitignore
3. Create agents/state.py
4. Create agents/prompts.py
5. Create agents/llm.py
6. Create agents/planner.py
7. Create agents/researcher.py
8. Create agents/graph.py
9. Create backend Django project structure
10. Create backend/config/settings/ files
11. Create backend/apps/conversations/models.py
12. Create backend/apps/conversations/serializers.py
13. Create backend/apps/conversations/views.py
14. Create backend/apps/conversations/urls.py
15. Create backend/config/urls.py
16. Create backend/manage.py
17. Create mcp/tools/search.py
18. Create mcp/server.py
19. Create ui/app.py
20. Create ui/.streamlit/config.toml
21. Create tests/test_agents.py
22. Create tests/test_api.py
23. Create tests/test_mcp.py
24. Create CLAUDE.md
25. Create README.md
26. Create Procfile

---

## TEST SUITE

### tests/test_agents.py — Test without LLM (use mocks)
```python
# Test 1: planner_node returns a plan
def test_planner_returns_plan(mocker):
    mocker.patch('agents.planner.get_llm').return_value.invoke.return_value.content = \
        "Need to search for: capital of France"
    result = planner_node({
        "user_question": "What is the capital of France?",
        "plan": None, "search_results": None, 
        "final_answer": None, "error": None
    })
    assert "plan" in result
    assert result["plan"] is not None

# Test 2: planner_node returns error on LLM failure  
def test_planner_handles_error(mocker):
    mocker.patch('agents.planner.get_llm').return_value.invoke.side_effect = \
        Exception("LLM failed")
    result = planner_node({...})
    assert "error" in result

# Test 3: researcher_node skips on error state
def test_researcher_skips_on_error():
    result = researcher_node({
        "user_question": "test", "plan": "test plan",
        "search_results": None, "final_answer": None,
        "error": "previous error"
    })
    assert result == {}

# Test 4: graph builds without error
def test_build_graph():
    graph = build_graph()
    assert graph is not None

# Test 5: graph runs end to end with mocked LLM
def test_graph_full_run(mocker):
    mock_llm = mocker.patch('agents.planner.get_llm').return_value
    mock_llm.invoke.return_value.content = "Need to search for: France capital"
    mocker.patch('agents.researcher.get_llm').return_value.invoke.return_value.content = \
        "Paris is the capital of France."
    graph = build_graph()
    result = graph.invoke({
        "user_question": "Capital of France?",
        "plan": None, "search_results": None,
        "final_answer": None, "error": None
    })
    assert result["final_answer"] is not None
```

### tests/test_api.py — Django API tests using TestCase
```python
# Test 1: POST /api/ask/ with valid question returns 200
def test_ask_question_success(mocker):
    mocker.patch('conversations.views.build_graph').return_value.invoke.return_value = {
        "plan": "search plan",
        "search_results": "some results", 
        "final_answer": "Paris",
        "error": None
    }
    response = client.post('/api/ask/', {"question": "capital of france?"})
    assert response.status_code == 200
    assert "answer" in response.json()

# Test 2: POST /api/ask/ with empty question returns 400
def test_ask_question_empty_returns_400():
    response = client.post('/api/ask/', {"question": ""})
    assert response.status_code == 400

# Test 3: POST /api/ask/ saves to database
def test_ask_saves_conversation(mocker):
    # mock graph, call endpoint, check Conversation.objects.count() == 1

# Test 4: GET /api/conversations/ returns list
def test_list_conversations():
    # Create 3 Conversation objects, call endpoint, check len == 3
```

### tests/test_mcp.py — MCP tool tests
```python
# Test 1: handle_search returns string for known topic
async def test_search_known_topic():
    result = await handle_search("capital france")
    assert isinstance(result, str)
    assert len(result) > 0

# Test 2: handle_search returns string for unknown topic  
async def test_search_unknown_topic():
    result = await handle_search("xyzzy unknown topic 12345")
    assert isinstance(result, str)

# Test 3: SEARCH_TOOL has required fields
def test_search_tool_schema():
    assert SEARCH_TOOL.name == "web_search"
    assert "query" in SEARCH_TOOL.inputSchema["properties"]
```

---

## VALIDATION COMMANDS
After building, run these in order:
```bash
# 1. Check all files exist
ls agents/ backend/ mcp/ ui/ tests/

# 2. Check imports work
cd assignment-1
python -c "from agents.state import ResearchState; print('state OK')"
python -c "from agents.llm import get_llm; print('llm OK')"
python -c "from agents.graph import build_graph; print('graph OK')"

# 3. Run unit tests (no real LLM needed)
pip install pytest pytest-mock pytest-asyncio
cd backend && python -m pytest ../tests/ -v

# 4. Django check
cd backend && python manage.py check

# 5. Test graph standalone
python agents/graph.py
```

All 5 must pass before considering the project built.

---

## DEFINITION OF DONE
The project is complete when:
- [ ] All files in FOLDER STRUCTURE exist
- [ ] `python -c "from agents.graph import build_graph"` works
- [ ] `python manage.py check` returns no errors
- [ ] All tests in tests/ pass
- [ ] `python agents/graph.py` prints a final answer