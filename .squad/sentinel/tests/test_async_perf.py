import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from five_card_poker.logic import Table, Player, PlayerType
from five_card_poker.ai import GeminiPokerAgent

@pytest.mark.asyncio
async def test_async_perf_slow_ai_does_not_block_read():
    """
    Test that a slow AI response does not block the event loop 
    for other operations like reading the game state.
    """
    # 1. Setup Game with AI Player
    game = Table()
    
    # Create a mock agent that sleeps
    mock_agent = MagicMock(spec=GeminiPokerAgent)
    
    async def slow_decision(*args, **kwargs):
        await asyncio.sleep(0.5)
        return "check", 0
        
    mock_agent.decide_betting_action = AsyncMock(side_effect=slow_decision)
    
    ai_player = Player(
        id="ai_1", 
        name="SlowBot", 
        type=PlayerType.AI, 
        balance=100, 
        agent=mock_agent
    )
    game.add_player(ai_player)
    
    # Start game to get into betting phase
    game.phase = "betting_1"
    game.active_player_idx = 0
    game.players[0].is_active = True
    game.players[0].is_folded = False
    
    # 2. Start the slow AI turn in the background
    # We use asyncio.create_task to simulate the concurrent nature of the server
    ai_task = asyncio.create_task(game.process_ai_turn())
    
    # 3. Measure time to get state
    start_time = time.time()
    
    # This represents a client polling for state while AI is thinking
    # It should happen immediately, not wait for the 0.5s sleep
    state = game.to_state("observer")
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 4. Assertions
    # The state retrieval should be near-instant, definitely under 0.1s
    assert duration < 0.1, f"State retrieval took too long: {duration}s"
    assert state.phase == "betting_1"
    
    # Wait for AI to finish to clean up
    await ai_task
