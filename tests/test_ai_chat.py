from unittest.mock import MagicMock, patch
from five_card_poker.ai import GeminiPokerAgent
from five_card_poker.models import PlayerState, TableState


def test_ai_chat_response_method_exists():
    agent = GeminiPokerAgent()
    assert hasattr(agent, "decide_chat_response")


@patch("google.generativeai.GenerativeModel.generate_content")
def test_ai_chat_response_generation(mock_generate):
    # Mock response
    mock_response = MagicMock()
    mock_response.text = '{"response": "I have a great hand!"}'
    mock_generate.return_value = mock_response

    agent = GeminiPokerAgent(api_key="fake")
    player_state = PlayerState(id="bot1", name="Bot 1", balance=100, type="ai")
    table_state = TableState(
        pot=10,
        current_bet=5,
        phase="betting_1",
        players=[],
        dealer_idx=0,
        deck_count=52,
        active_player_id="bot1",
    )

    response = agent.decide_chat_response("Nice hand!", [], player_state, table_state)
    assert response == "I have a great hand!"


def test_chat_trigger_in_main():
    # This would be a functional test using TestClient
    from fastapi.testclient import TestClient
    from five_card_poker.main import app, table

    client = TestClient(app)

    # Mock the agents to avoid real API calls
    for p in table.players:
        if p.type == "AI" and p.agent:
            p.agent.decide_chat_response = MagicMock(return_value="Bot says hello")

    with patch("random.random", return_value=0.1):
        response = client.post(
            "/chat/send", json={"player_id": "player1", "text": "Hello bots"}
        )
        assert response.status_code == 200

    # Check if a bot replied
    chat_response = client.get("/chat/messages")
    messages = chat_response.json()

    # We expect player1's message AND at least one bot reply
    assert len(messages) >= 2
    assert any(msg["player_id"] in ["bot1", "bot2"] for msg in messages)
