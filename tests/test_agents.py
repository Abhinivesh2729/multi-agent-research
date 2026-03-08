"""Tests for agent functionality (using mocks, no real LLM)."""
import pytest
from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.graph import build_graph


def test_planner_returns_plan(mocker):
    """Test 1: planner_node returns a plan."""
    mock_llm = mocker.patch('agents.planner.get_llm')
    mock_response = mocker.Mock()
    mock_response.content = "Need to search for: capital of France"
    mock_llm.return_value.invoke.return_value = mock_response

    result = planner_node({
        "user_question": "What is the capital of France?",
        "plan": None,
        "search_results": None,
        "final_answer": None,
        "error": None
    })

    assert "plan" in result
    assert result["plan"] is not None
    assert "capital of France" in result["plan"]


def test_planner_handles_error(mocker):
    """Test 2: planner_node returns error on LLM failure."""
    mock_llm = mocker.patch('agents.planner.get_llm')
    mock_llm.return_value.invoke.side_effect = Exception("LLM failed")

    result = planner_node({
        "user_question": "What is the capital of France?",
        "plan": None,
        "search_results": None,
        "final_answer": None,
        "error": None
    })

    assert "error" in result
    assert "LLM failed" in result["error"]


def test_researcher_skips_on_error():
    """Test 3: researcher_node skips on error state."""
    result = researcher_node({
        "user_question": "test",
        "plan": "test plan",
        "search_results": None,
        "final_answer": None,
        "error": "previous error"
    })

    assert result == {}


def test_build_graph():
    """Test 4: graph builds without error."""
    graph = build_graph()
    assert graph is not None


def test_researcher_includes_mcp_invocation_in_steps(mocker):
    """Test 5: researcher output explicitly records MCP tool invocation."""
    mock_llm = mocker.patch('agents.researcher.get_llm')
    mock_response = mocker.Mock()
    mock_response.content = "Sample synthesized answer"
    mock_llm.return_value.invoke.return_value = mock_response

    result = researcher_node({
        "user_question": "Who is Mr Abhi?",
        "plan": "Need to search for: Mr Abhi",
        "search_results": None,
        "final_answer": None,
        "error": None
    })

    assert "search_results" in result
    assert "MCP Tool Invocation: web_search" in result["search_results"]
    assert "final_answer" in result


def test_graph_full_run(mocker):
    """Test 6: graph runs end to end with mocked LLM."""
    # Mock planner LLM
    mock_planner_llm = mocker.patch('agents.planner.get_llm')
    mock_planner_response = mocker.Mock()
    mock_planner_response.content = "Need to search for: France capital"
    mock_planner_llm.return_value.invoke.return_value = mock_planner_response

    # Mock researcher LLM
    mock_researcher_llm = mocker.patch('agents.researcher.get_llm')
    mock_researcher_response = mocker.Mock()
    mock_researcher_response.content = "Paris is the capital of France."
    mock_researcher_llm.return_value.invoke.return_value = mock_researcher_response

    graph = build_graph()
    result = graph.invoke({
        "user_question": "Capital of France?",
        "plan": None,
        "search_results": None,
        "final_answer": None,
        "error": None
    })

    assert result["final_answer"] is not None
    assert "Paris" in result["final_answer"]
