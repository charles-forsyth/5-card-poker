import pytest
from unittest.mock import MagicMock

# This conftest.py is part of the Sentinel's QA strategy.
# It provides shared fixtures for the test suite.
# Since the backend code is not yet implemented, we mock the core components.


@pytest.fixture
def mock_deck():
    """Fixture providing a mock Deck object."""
    deck = MagicMock()
    deck.cards = [MagicMock() for _ in range(52)]
    deck.shuffle = MagicMock()
    return deck


@pytest.fixture
def mock_game_engine():
    """Fixture providing a mock GameEngine."""
    engine = MagicMock()
    engine.start_game.return_value = "game-id-123"
    engine.draw_phase.return_value = {"phase": "draw", "player_id": "p1"}
    engine.get_state.return_value = {"phase": "deal", "players": []}
    return engine


@pytest.fixture
def mock_app():
    """Fixture providing a mock FastAPI app."""
    app = MagicMock()
    return app


@pytest.fixture
def client(mock_app):
    """Fixture providing a mock TestClient for the API."""
    client = MagicMock()
    # Mocking client methods to simulate API responses
    post_response = MagicMock()
    post_response.status_code = 200
    post_response.json.return_value = {"game_id": "mock-id", "state": {}}
    client.post.return_value = post_response

    get_response = MagicMock()
    get_response.status_code = 200
    get_response.json.return_value = {"state": "mock-state"}
    client.get.return_value = get_response

    return client
