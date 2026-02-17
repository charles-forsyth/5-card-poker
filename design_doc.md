# Design Doc: AI Chat and Game Flow Fixes

## Problem
1. AI bots do not respond to chat messages.
2. The game reportedly gets stuck in the "Waiting" phase.

## Proposed Changes

### 1. AI Chat Implementation
- **GeminiPokerAgent**: Add a `decide_chat_response` method. This method will take the latest chat message and game context (state) to generate a short, persona-driven response.
- **ChatManager**: Add a method to get recent chat history for context.
- **Main App**: In the `send_chat_message` endpoint, trigger a response from one or more AI players. To avoid blocking the request, this could be handled by a background task, but for simplicity in this project, we can trigger it sequentially after the message is added, or have the client poll for new messages.

### 2. Game Flow Fixes (Waiting Phase)
- **Investigate `waiting` phase**: The phase `waiting` is intended for when a hand is over and the game is waiting for a new "Deal" (ante).
- **Potential Issue**: If a hand ends (everyone folds or showdown), it transitions to `waiting`. If the UI doesn't show the result clearly or if the "Deal" button is disabled/hidden, the user might feel "stuck".
- **Improvement**: 
    - Ensure `_showdown` and `_end_hand` provide clear feedback via chat/log.
    - Check for any state where `phase` is `waiting` but `dealBtn` might not be visible.
    - Add a "Showdown" state that persists until the user acknowledges it (optional, but might help). 
    - For now, I will ensure that if the human is out of chips, they get a notification, and I'll add a "Reset Game" button to the UI.

## Implementation Plan
1. **Sentinel**: Write tests for AI chat and game state transitions.
2. **DevOps**: Bump version in `pyproject.toml`.
3. **Grunt**: 
    - Update `GeminiPokerAgent` in `ai.py` with `decide_chat_response`.
    - Update `Table` and `main.py` to trigger bot chat.
    - Add "Reset Game" button to `index.html` and `script.js`.
    - Fix any logic errors in `logic.py` preventing phase advancement.
4. **Gatekeeper**: Audit and merge.
5. **UAT**: Verify fixes.
