"""Django API tests."""
import pytest
from django.test import Client
from conversations.models import Conversation


@pytest.fixture
def client():
    """Create a test client."""
    return Client()


@pytest.mark.django_db
def test_ask_question_success(mocker, client):
    """Test 1: POST /api/ask/ with valid question returns 200."""
    mock_graph = mocker.patch('conversations.views.build_graph')
    mock_graph.return_value.invoke.return_value = {
        "plan": "search plan",
        "search_results": "some results",
        "final_answer": "Paris",
        "error": None
    }

    response = client.post(
        '/api/ask/',
        {"question": "capital of france?"},
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Paris"


@pytest.mark.django_db
def test_ask_question_empty_returns_400(client):
    """Test 2: POST /api/ask/ with empty question returns 400."""
    response = client.post(
        '/api/ask/',
        {"question": ""},
        content_type='application/json'
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_ask_saves_conversation(mocker, client):
    """Test 3: POST /api/ask/ saves to database."""
    mock_graph = mocker.patch('conversations.views.build_graph')
    mock_graph.return_value.invoke.return_value = {
        "plan": "search plan",
        "search_results": "results",
        "final_answer": "answer",
        "error": None
    }

    initial_count = Conversation.objects.count()

    response = client.post(
        '/api/ask/',
        {"question": "test question"},
        content_type='application/json'
    )

    assert response.status_code == 200
    assert Conversation.objects.count() == initial_count + 1


@pytest.mark.django_db
def test_list_conversations(client):
    """Test 4: GET /api/conversations/ returns list."""
    # Create 3 conversations
    for i in range(3):
        Conversation.objects.create(
            question=f"Question {i}",
            plan=f"Plan {i}",
            search_results=f"Results {i}",
            answer=f"Answer {i}"
        )

    response = client.get('/api/conversations/')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
