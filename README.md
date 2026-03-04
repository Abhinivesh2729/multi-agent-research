# Multi-Agent Research Assistant

A conversational research assistant powered by LangGraph multi-agent orchestration, Django REST API backend, and Streamlit chat UI.

## Features

- **Multi-Agent System**: Planner and Researcher agents work together to answer questions
- **LangGraph Orchestration**: State-based workflow with conditional routing
- **REST API**: Django backend with conversation storage
- **Chat UI**: Streamlit interface with agent step visibility
- **Flexible LLM Support**: Works with Ollama (local) or Groq (cloud)
- **MCP Integration**: Model Context Protocol server for search tools

## Tech Stack

- **Python 3.11**
- **LLM**: Ollama (qwen2.5:3b) via langchain-ollama
- **Agents**: LangChain + LangGraph
- **Backend**: Django 4.2 + Django REST Framework
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **MCP**: mcp Python package

## Project Structure

```
├── agents/              # LangGraph agent definitions
│   ├── state.py        # ResearchState TypedDict
│   ├── llm.py          # LLM provider abstraction
│   ├── prompts.py      # System prompts
│   ├── planner.py      # Planner agent
│   ├── researcher.py   # Researcher agent
│   └── graph.py        # LangGraph workflow
├── backend/            # Django REST API
│   ├── config/         # Django settings
│   └── apps/
│       └── conversations/  # Conversation model and views
├── mcp/                # MCP server
│   ├── server.py       # MCP server implementation
│   └── tools/
│       └── search.py   # Mock search tool
├── ui/                 # Streamlit UI
│   └── app.py
└── tests/              # Test suite
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Ollama (or Groq API key)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

### Running the Application

1. **Start the Django backend:**
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Start the Streamlit UI** (in another terminal):
   ```bash
   streamlit run ui/app.py
   ```

3. **Access the UI:**
   Open http://localhost:8501 in your browser

### Testing

Run the test suite:
```bash
cd backend
python -m pytest ../tests/ -v
```

Test the agent graph standalone:
```bash
python agents/graph.py
```

Check Django configuration:
```bash
cd backend
python manage.py check
```

## How It Works

1. **User asks a question** via Streamlit UI
2. **Planner agent** analyzes the question and determines what to search for
3. **Researcher agent** performs the search and synthesizes an answer
4. **Result is saved** to PostgreSQL via Django API
5. **Answer is displayed** in the chat UI with agent steps visible

## Environment Variables

See `.env.example` for all configuration options:

- `LLM_PROVIDER`: "ollama" or "groq"
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: Model name (default: qwen2.5:3b)
- `GROQ_API_KEY`: Groq API key (if using Groq)
- `DATABASE_URL`: PostgreSQL connection string
- `DJANGO_API_URL`: Backend URL (default: http://localhost:8000)

## Development

See `CLAUDE.md` for detailed development instructions and architecture notes.

## License

MIT
