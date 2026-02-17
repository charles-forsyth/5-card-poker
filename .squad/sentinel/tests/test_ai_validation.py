import pytest
from unittest.mock import AsyncMock, MagicMock
from five_card_poker.logic import Table, Player, PlayerType
from five_card_poker.ai import GeminiPokerAgent


@pytest.mark.asyncio
async def test_ai_validation_handles_illegal_raise():
    """
    Test that if an AI agent returns an illegal action (e.g., betting more chips than it has),
    the logic handles it gracefully (forces a Fold or Check).
    """
    # 1. Setup Game with AI Player
    game = Table()
    game.phase = "betting_1"

    # Mock an AI agent that returns an invalid move
    mock_agent = MagicMock(spec=GeminiPokerAgent)
    # Return "raise" with an amount exceeding balance (balance defaults to 100)
    mock_agent.decide_betting_action = AsyncMock(return_value=("raise", 1000))

    ai_player = Player(
        id="ai_invalid",
        name="BadBot",
        type=PlayerType.AI,
        balance=100,
        agent=mock_agent,
    )
    game.add_player(ai_player)

    # Add a dummy opponent so the hand doesn't end immediately
    dummy_opponent = Player(id="p2", name="Dummy", type=PlayerType.HUMAN, balance=100)
    game.add_player(dummy_opponent)

    # Set up game state where a check is valid (current_bet == player_bet)
    game.current_bet = 0
    ai_player.current_bet = 0
    dummy_opponent.current_bet = 0
    game.active_player_idx = 0
    ai_player.is_active = True
    ai_player.is_folded = False
    dummy_opponent.is_active = True
    dummy_opponent.is_folded = False

    # 2. Trigger the AI turn
    await game.process_ai_turn()

    # 3. Assertions
    # The raise should fail, fallback to check
    assert ai_player.last_action == "Check", (
        f"Expected fallback to 'Check', got '{ai_player.last_action}'"
    )
    assert ai_player.is_folded is False


@pytest.mark.asyncio
async def test_ai_validation_handles_illegal_check_fallback_to_fold():
    """
    Test that if an AI tries to check when it cannot (e.g., facing a bet),
    and also fails the primary action, it falls back to Fold.
    """
    # 1. Setup Game
    game = Table()
    game.phase = "betting_1"

    mock_agent = MagicMock(spec=GeminiPokerAgent)
    # Return "check" when facing a bet (invalid)
    mock_agent.decide_betting_action = AsyncMock(return_value=("check", 0))

    ai_player = Player(
        id="ai_invalid_2",
        name="BadBot2",
        type=PlayerType.AI,
        balance=100,
        agent=mock_agent,
    )
    game.add_player(ai_player)

    # Set up game state where check is INVALID (current_bet > player_bet)
    game.current_bet = 50
    ai_player.current_bet = 0
    game.active_player_idx = 0
    ai_player.is_active = True
    ai_player.is_folded = False

    # 2. Trigger AI turn
    await game.process_ai_turn()

    # 3. Assertions
    # The check should fail, fallback to fold
    assert ai_player.is_folded is True, "Expected player to fold after invalid check"
    assert ai_player.last_action == "Fold"
