# Design Document: 5-Card Poker - Reliability & AI Upgrade

## 1. Executive Summary
This document outlines the architectural overhaul required to address critical stability issues (Draw Phase Freeze, Deck Shuffle Bug) and implement Dynamic AI Player Count. The proposed solution shifts the core game logic from the frontend to a robust, testable Python backend using FastAPI.

## 2. Problem Analysis

### 2.1 Draw Phase Freeze
**Root Cause Hypothesis:** Complex state mutations in the frontend (likely within a `useEffect` or deep prop drilling) are causing race conditions or infinite re-render loops during the draw phase.
**Solution:** Decouple game state from UI rendering. The frontend should purely reflect the state provided by the backend.

### 2.2 Deck Shuffle Bug
**Root Cause Hypothesis:** JavaScript's `Math.random()` or incorrect array mutation in React state is leading to predictable or failed shuffles.
**Solution:** Utilize Python's `random.shuffle()` (Mersenne Twister) or `secrets` module for cryptographically secure, robust shuffling on the server.

### 2.3 Dynamic AI Player Count
**Requirement:** Support a variable number of AI opponents.
**Solution:** Parameterize the `GameEngine` initialization to accept `num_players`. The backend will instantiate `AIPlayer` objects dynamically.

## 3. Proposed Architecture

### 3.1 Backend-First Approach (The "Skywalker" Pattern)
We will implement a Python-based Game Engine packaged with `uv`.

**Directory Structure:**
```text
backend/
├── pyproject.toml         # Project metadata & dependencies
├── src/
│   └── poker_engine/
│       ├── __init__.py
│       ├── engine.py      # Core Game Loop & State Machine
│       ├── deck.py        # Deck & Card Classes
│       ├── player.py      # Human & AI Player Logic
│       └── api.py         # FastAPI Routes
└── tests/
    ├── test_engine.py
    └── test_deck.py
```

### 3.2 API Contract (FastAPI)

*   `POST /game/start`: Initializes a new game.
    *   Body: `{ "human_players": 1, "ai_players": N }`
    *   Response: `{ "game_id": "uuid", "state": { ... } }`
*   `POST /game/{game_id}/draw`: Triggers the draw phase for a player.
    *   Body: `{ "player_id": "pid", "cards_to_discard": [indices] }`
    *   Response: Updated Game State.
*   `GET /game/{game_id}/state`: Polling endpoint for UI updates (or WebSocket upgrade).

## 4. Implementation Details

### 4.1 The Deck (Fixing the Shuffle)
```python
# src/poker_engine/deck.py
import random
from enum import Enum

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for s in Suit for r in Rank]
    
    def shuffle(self):
        # Reliable, in-place shuffle
        random.shuffle(self.cards)
```

### 4.2 Dynamic AI (New Feature)
The `GameEngine` will iterate `n` times to create AI players.
```python
# src/poker_engine/engine.py
def __init__(self, ai_count: int):
    self.players = [HumanPlayer()]
    for i in range(ai_count):
        self.players.append(AIPlayer(difficulty="adaptive"))
```

## 5. Architectural Decision Records (ADRs)

### ADR-001: Python Backend for Game Logic
*   **Status:** Accepted
*   **Context:** Frontend-heavy logic has led to freezing and state bugs.
*   **Decision:** Move all authoritative game state (Deck, Hands, Turn Order) to a Python FastAPI backend.
*   **Consequences:**
    *   (+) **Reliability:** Python's data structures are robust for game state.
    *   (+) **Testability:** `pytest` can verify the Shuffle and Draw logic in isolation, preventing regressions.
    *   (-) **Complexity:** Requires running a backend server.

### ADR-002: Stateless Frontend
*   **Status:** Proposed
*   **Context:** UI rendering is tightly coupled with game logic, causing freezes.
*   **Decision:** The Frontend (Next.js/React) will act as a "View" only. It will render the state returned by the API.
*   **Consequences:** eliminates render-loop freezes caused by complex state calculations in the browser.

### ADR-003: Packaging with `uv`
*   **Status:** Mandated
*   **Context:** We need a reproducible environment.
*   **Decision:** Use `uv` for dependency management and running the dev server.
