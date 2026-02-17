import pytest
from unittest.mock import AsyncMock, patch, MagicMock
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
def mock_genai_client():
    with patch("google.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        # The new SDK uses client.aio.models.generate_content
        mock_client.aio = MagicMock()
        mock_client.aio.models = MagicMock()
        mock_client.aio.models.generate_content = AsyncMock()
        yield mock_client


@pytest.fixture
def agent(mock_genai_client):
    return GeminiPokerAgent(api_key="fake_key")


@pytest.mark.asyncio
async def test_decide_betting_action_call(agent, mock_genai_client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"action": "call", "amount": 0}'
    mock_genai_client.aio.models.generate_content.return_value = mock_response

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

    action, amount = await agent.decide_betting_action(player_state, table_state)

    assert action == "call"
    assert amount == 0


@pytest.mark.asyncio
async def test_decide_betting_action_raise(agent, mock_genai_client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"action": "raise", "amount": 20}'
    mock_genai_client.aio.models.generate_content.return_value = mock_response

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

    action, amount = await agent.decide_betting_action(player_state, table_state)

    assert action == "raise"
    assert amount == 20


@pytest.mark.asyncio
async def test_decide_draw_action(agent, mock_genai_client):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"held_indices": [0, 1, 4]}'
    mock_genai_client.aio.models.generate_content.return_value = mock_response

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

    held_indices = await agent.decide_draw_action(player_state, table_state)

    assert held_indices == [0, 1, 4]
