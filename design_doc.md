# Design Doc: Fix Held Cards Refresh and Game State Transitions

## Problem
1. `Table.handle_draw` does not advance the game phase or turn, causing the game to hang in the "drawing" phase.
2. `held_indices` might be misinterpreted if the turn doesn't advance.
3. `GameLogic` legacy class has an empty deck on initialization, causing test failures.
4. `test_poker.py` has outdated expectations for the API response format.

## Proposed Changes

### 1. `src/five_card_poker/logic.py`
- **`GameLogic.__init__`**: Call `self.shuffle()` to populate the deck.
- **`Table.handle_draw`**: 
    - Add phase check (`assert self.phase == "drawing"`).
    - Add null check for `player.hand`.
    - Advance to the next player after drawing.
    - Transition to `betting_2` phase after all active players have drawn.
- **`Table._advance_turn_drawing`**: New helper to manage drawing turn transitions.

### 2. `src/five_card_poker/main.py`
- Update `/draw` to automatically handle AI drawing turns until it's the human's turn again or the phase changes.

### 3. `tests/test_poker.py`
- Update API tests to match the `TableState` schema (e.g., check `players[0].hand.cards` instead of top-level `cards`).
- Adjust expected phase in `test_api_bet` if needed, or modify `Table.start_game` to skip `betting_1` if only one player is active (though we have bots, so `betting_1` is correct).

## Verification Plan
- Run `uv run pytest`.
- Specifically check `test_drawing_round` in `tests/test_multiplayer.py`.
- Manual verification in the UI.
