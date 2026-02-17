import pytest
import sys
import os
from unittest.mock import MagicMock

# This conftest.py is part of the Sentinel's QA strategy.
# It provides shared fixtures for the test suite.

# Add the project source directory to sys.path so tests can import modules
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src"))
)


@pytest.fixture
def mock_card():
    """Provides a mock card object."""
    card = MagicMock()
    card.suit = "hearts"
    card.rank = 10
    return card


@pytest.fixture
def mock_hand():
    """Provides a mock hand containing 5 mock cards."""
    cards = []
    for i in range(5):
        card = MagicMock()
        card.rank = i + 2
        card.suit = "clubs"
        cards.append(card)
    return cards


@pytest.fixture
def game_state():
    """Provides a basic mock of the GameState."""
    state = MagicMock()
    state.pot = 0
    state.currentPhase = "deal"
    state.players = []
    return state


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
