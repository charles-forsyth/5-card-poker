import pytest
from fastapi.testclient import TestClient
from five_card_poker.main import app
from five_card_poker.ai import GeminiPokerAgent


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_gemini_agent(monkeypatch, request):
    """
    Mock GeminiPokerAgent globally for all tests EXCEPT test_ai_player.py.
    This ensures integration tests pass with deterministic bot behavior,
    while unit tests can test the actual agent logic.
    """
    if "test_ai_player" in request.node.name or "test_ai_player" in str(request.fspath):
        return

    def mock_decide_betting(self, player_state, table_state):
        return "call", 0

    def mock_decide_draw(self, player_state, table_state):
        return []

    monkeypatch.setattr(GeminiPokerAgent, "decide_betting_action", mock_decide_betting)
    monkeypatch.setattr(GeminiPokerAgent, "decide_draw_action", mock_decide_draw)
