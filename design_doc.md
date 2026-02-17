# Design Doc: Gemini-Powered AI Poker Players

## Objective
Replace the hardcoded, simple AI in the 5-card draw poker game with intelligent agents powered by Google's **Gemini 2.5 Flash** model.

## Architecture

### 1. New Component: `src/five_card_poker/ai.py`
This module will handle all interactions with the Gemini API.

*   **Class `GeminiPokerAgent`**:
    *   **Responsibilities**:
        *   Construct prompts based on current game state (hand, pot, betting history).
        *   Call `google.generativeai` API.
        *   Parse the JSON response to determine actions (Bet/Fold/Call/Raise, Draw cards).
    *   **Methods**:
        *   `decide_betting_action(self, game_context: dict) -> dict`: Returns `{"action": "raise", "amount": 20}`.
        *   `decide_draw_action(self, game_context: dict) -> list[int]`: Returns indices of cards to hold.

### 2. Integration: `src/five_card_poker/logic.py`
*   **`Player` Class**:
    *   Add an optional `agent` attribute (type `GeminiPokerAgent`).
*   **`Table` Class**:
    *   Add `process_ai_turn()`: A helper method to execute the AI's logic.
    *   Refactor `handle_action` and `handle_draw` to be more robust.

### 3. Application Logic: `src/five_card_poker/main.py`
*   Initialize `Table` with `GeminiPokerAgent` instances for AI players.
*   Update endpoints (`/action`, `/draw`, `/bet`) to call `table.process_ai_turns()` instead of the current hardcoded `while` loops.
*   **Environment**: Load `GEMINI_API_KEY` from environment variables.

## Prompt Engineering
The prompt will describe the poker hand and game state in natural language.
*   *Input*: "You are a poker pro. Hand: [Ah, Kh, Qh, Jh, 10h]. Pot: 100. Call cost: 10. Phase: Betting 1. Opponents: Player 1 (Human) checked. What is your move? Respond in JSON: {action, amount}."
*   *Output*: JSON strict mode.

## Dependencies
*   `google-generativeai`

## Testing Plan
*   Mock `google.generativeai.GenerativeModel.generate_content` to return canned responses for testing logic without spending tokens/latency.
