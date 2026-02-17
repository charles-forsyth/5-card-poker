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

---

# Design Update: Opponent Feedback & Player Chat

## Objective
Enhance player experience by providing clear feedback on opponent actions and enabling player-to-player communication.

## Architecture

### 1. Chat System (`src/five_card_poker/chat.py`)
*   **Class `ChatManager`**:
    *   **Responsibilities**:
        *   Store chat messages in memory.
        *   Provide methods to add and retrieve messages.
    *   **Attributes**:
        *   `messages: List[ChatMessage]`
*   **Model `ChatMessage`**:
    *   `id: str` (uuid)
    *   `player_id: str` (e.g., "player1", "system")
    *   `text: str`
    *   `timestamp: float`

### 2. Game Logic Integration (`src/five_card_poker/logic.py`)
*   **`Table` Class**:
    *   Accept an optional `chat_manager` instance.
    *   Log game events (e.g., "Player 1 bets 10", "Bot 2 folds") to the chat manager as system messages.
    *   Update `handle_action`, `handle_draw`, `_showdown`, `_end_hand` to log events.

### 3. API Endpoints (`src/five_card_poker/main.py`)
*   **`POST /chat/send`**:
    *   Input: `{"player_id": str, "text": str}`
    *   Action: Add message to `ChatManager`.
*   **`GET /chat/messages`**:
    *   Output: List of messages.

### 4. Frontend (`index.html`, `script.js`)
*   **UI**:
    *   Add a chat box container (messages area, input field, send button).
    *   Style messages differently based on sender (e.g., system messages in italics, user messages aligned right).
*   **Logic**:
    *   Poll `/chat/messages` every few seconds (e.g., 2s).
    *   Send message on button click or Enter key.
    *   Auto-scroll to bottom on new messages.
