import pytest
from unittest.mock import MagicMock, patch
from five_card_poker.ai import GeminiPokerAgent
from five_card_poker.models import (
    Card,
    Suit,
    Rank,
    Hand,
    PlayerState,
    TableState,
    PlayerType,
)


@pytest.fixture
def mock_gemini_model():
    with patch("google.generativeai.GenerativeModel") as MockModel:
        mock_instance = MockModel.return_value
        yield mock_instance


@pytest.fixture
def agent(mock_gemini_model):
    return GeminiPokerAgent(api_key="fake_key")


def test_decide_betting_action_call(agent, mock_gemini_model):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"action": "call", "amount": 0}'
    mock_gemini_model.generate_content.return_value = mock_response

    # Test context
    hand = Hand(
        cards=[Card(suit=Suit.HEARTS, rank=Rank.ACE)], rank="High Card", score=14
    )
    player_state = PlayerState(
        id="bot1",
        name="Bot 1",
        type=PlayerType.AI,
        balance=100,
        hand=hand,
        is_folded=False,
        current_bet=0,
        last_action="",
        is_active=True,
    )
    table_state = TableState(
        players=[player_state],
        pot=10,
        current_bet=10,
        phase="betting_1",
        active_player_id="bot1",
        dealer_idx=0,
        deck_count=47,
    )

    action, amount = agent.decide_betting_action(player_state, table_state)

    assert action == "call"
    assert amount == 0  # Amount is irrelevant for call usually, handled by logic


def test_decide_betting_action_raise(agent, mock_gemini_model):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"action": "raise", "amount": 20}'
    mock_gemini_model.generate_content.return_value = mock_response

    # Test context
    hand = Hand(
        cards=[Card(suit=Suit.HEARTS, rank=Rank.ACE)], rank="High Card", score=14
    )
    player_state = PlayerState(
        id="bot1",
        name="Bot 1",
        type=PlayerType.AI,
        balance=100,
        hand=hand,
        is_folded=False,
        current_bet=0,
        last_action="",
        is_active=True,
    )
    table_state = TableState(
        players=[player_state],
        pot=10,
        current_bet=10,
        phase="betting_1",
        active_player_id="bot1",
        dealer_idx=0,
        deck_count=47,
    )

    action, amount = agent.decide_betting_action(player_state, table_state)

    assert action == "raise"
    assert amount == 20


def test_decide_draw_action(agent, mock_gemini_model):
    # Setup mock response
    mock_response = MagicMock()
    # Indices 0, 1, 4 to be held
    mock_response.text = '{"held_indices": [0, 1, 4]}'
    mock_gemini_model.generate_content.return_value = mock_response

    # Test context
    hand = Hand(
        cards=[
            Card(suit=Suit.HEARTS, rank=Rank.ACE),
            Card(suit=Suit.DIAMONDS, rank=Rank.ACE),
            Card(suit=Suit.CLUBS, rank=Rank.TWO),
            Card(suit=Suit.SPADES, rank=Rank.THREE),
            Card(suit=Suit.HEARTS, rank=Rank.KING),
        ],
        rank="One Pair",
        score=100,
    )

    player_state = PlayerState(
        id="bot1",
        name="Bot 1",
        type=PlayerType.AI,
        balance=100,
        hand=hand,
        is_folded=False,
        current_bet=0,
        last_action="",
        is_active=True,
    )
    table_state = TableState(
        players=[player_state],
        pot=10,
        current_bet=0,
        phase="drawing",
        active_player_id="bot1",
        dealer_idx=0,
        deck_count=47,
    )

    held_indices = agent.decide_draw_action(player_state, table_state)

    assert held_indices == [0, 1, 4]
