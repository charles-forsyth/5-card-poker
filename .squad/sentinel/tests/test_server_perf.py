import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from five_card_poker.main import app
from five_card_poker.models import PlayerType
from five_card_poker.logic import Table, Player
from five_card_poker.ai import GeminiPokerAgent


@pytest.mark.asyncio
async def test_server_perf_slow_ai_does_not_block_state():
    """
    Integration test to verify that a slow AI turn (triggered by /action)
    does not block a concurrent /state request.

    This test is expected to FAIL with the current implementation
    due to the global async lock in main.py.
    """
    # 1. Setup App State
    # Initialize the table manually
    table = Table()
    app.state.table = table
    app.state.chat_manager = MagicMock()  # Mock chat manager

    human = Player(id="p1", name="Human", type=PlayerType.HUMAN, balance=100)

    # Mock AI Agent to sleep for 1.0 second
    mock_agent = MagicMock(spec=GeminiPokerAgent)

    async def slow_decision(*args, **kwargs):
        await asyncio.sleep(1.0)
        return "call", 0

    mock_agent.decide_betting_action = AsyncMock(side_effect=slow_decision)

    ai = Player(id="ai1", name="Bot", type=PlayerType.AI, balance=100, agent=mock_agent)

    table.add_player(human)
    table.add_player(ai)

    # Start game (Ante 5)
    # This deals cards and sets phase to betting_1
    table.start_game(ante=5)

    # Force turn order: Human -> AI
    # Ensure Human is active and it's their turn
    table.active_player_idx = 0
    assert table.players[0].id == "p1"

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 2. Trigger slow AI turn via Human Action
        # Human calls. Next player is AI.
        # main.py loop: while AI -> process_ai_turn (which sleeps 1s)
        action_payload = {"player_id": "p1", "action": "call", "amount": 0}

        start_time = time.time()

        # Fire and forget (create task) for the blocking action
        action_task = asyncio.create_task(client.post("/action", json=action_payload))

        # Allow the request to hit the server and acquire the lock
        await asyncio.sleep(0.1)

        # 3. Request State concurrently
        # If the server is blocking, this will hang until action_task finishes (approx 1s)
        state_resp = await client.get("/state?player_id=p1")

        end_time = time.time()
        duration = end_time - start_time

        assert state_resp.status_code == 200

        # Cleanup
        await action_task

        # 4. Verify Performance
        # We expect this to fail if the duration is ~1.0s
        print(f"State request took {duration:.4f}s")
        assert duration < 0.5, (
            f"State request was blocked! Took {duration:.4f}s. Expected < 0.5s"
        )
