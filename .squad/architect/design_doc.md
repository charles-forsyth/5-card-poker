# Design Document: Stability & Performance Upgrades

## 1. Executive Summary
This document outlines the technical design for a major refactoring of the `5-card-poker` application. The primary objectives are to unblock the server during AI processing, modernize the technology stack, and harden the core game logic against edge cases.

## 2. Goal 1: Asynchronous AI State Machine
**Current Issue:**
The current implementation uses a `while` loop inside the primary `table._lock` within API handlers (`/action`, `/bet`, `/draw`). This holds the lock while waiting for slow LLM API calls, causing the server to freeze for all other requests (including `/state` polling).

**Proposed Solution:**
Decouple the *decision* to process an AI turn from the *execution* of that turn. We will implement an "AI Loop" that runs as a background task, triggered whenever the game state transitions to an AI player's turn.

### 2.1 The "Background Loop" Pattern
1.  **Trigger:** When a human player completes an action (or the game starts), `Table._advance_turn()` is called.
2.  **Check:** If the `active_player` is an AI, the system **does not** immediately await `process_ai_turn()`.
3.  **Signal:** Instead, it fires an `asyncio.Event` or adds a task to an `asyncio.Queue`.
4.  **Worker:** A dedicated, long-running background task (`ai_worker`) waits for this signal.
    *   **Step A (Read):** Acquire Lock -> Read/Copy Game State -> Release Lock.
    *   **Step B (Think):** Call LLM API (No Lock held). This is the slow part.
    *   **Step C (Act):** Acquire Lock -> Validate Turn (ensure game hasn't changed invalidly) -> Apply Action -> Release Lock.
    *   **Step D (Loop):** If next player is also AI, repeat immediately.

### 2.2 Sequence Diagram
```text
Human Request (/action)
   |
   +-> [Lock] Update State -> Next Player is AI? -> [Signal Worker] -> [Unlock] -> Return 200 OK
                                      |
Background Worker --------------------+
   |
   +-> Wait for Signal
   +-> [Lock] Get Snapshot [Unlock]
   +-> Call Gemini API (Slow, Non-blocking)
   +-> [Lock] Apply Move -> Next Player is AI? -> [Signal Self] -> [Unlock]
```

## 3. Goal 2: Modernization & Deprecations

### 3.1 FastAPI Lifespan Events
**Current:** Uses deprecated `@app.on_event("startup")`.
**New:** Use the `contextlib.asynccontextmanager` pattern.
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_game_state()
    # Start AI Worker Task
    yield
    # Shutdown logic (Cancel Worker)
```

### 3.2 Google GenAI SDK
**Current:** `google-generativeai` (v1/v2).
**New:** `google-genai` (Modern SDK).
*   Update `GeminiPokerAgent` to use the new client signature.
*   Ensure proper error handling for the new SDK's exceptions.

## 4. Goal 3: Logic Robustness

### 4.1 Refactoring `_advance_turn`
The current `_advance_turn` method mixes phase transition logic with player iteration.
**Refactor:**
*   Split into `_next_active_player()` and `_check_phase_transition()`.
*   `_check_phase_transition()` should explicitly handle:
    *   `Betting 1` -> `Drawing`
    *   `Drawing` -> `Betting 2`
    *   `Betting 2` -> `Showdown`
    *   `Showdown` -> `Reset/Waiting`

### 4.2 Hand Evaluation Optimization
**Current:** `evaluate_hand` creates multiple lists and sorts repeatedly.
**Optimization:**
*   Pre-calculate `Rank` and `Suit` integer values.
*   Use bitwise operations or optimized lookups for hand checking if performance profiling shows bottlenecks.
*   Cache evaluation results on the `Hand` object so they aren't re-calculated on every state read.

## 5. Goal 4: Stricter Type Hinting

### 5.1 Actions Plan
*   Enable `mypy` strict mode in `pyproject.toml`.
*   Replace `dict` returns in `to_state` methods with Pydantic `BaseModel` schemas (already partially done, but needs enforcement).
*   Add generic types for Lists (e.g., `List[Card]` instead of `list`).
*   Ensure `Optional` types are handled with explicit `None` checks.

## 6. Implementation Plan
1.  **Refactor Logic:** Update `logic.py` first to support the new `_advance_turn` structure and strict types.
2.  **Update Dependencies:** Switch SDKs and fix `main.py` lifespan.
3.  **Implement Async Worker:** Add the `ai_worker` to `main.py` and hook it into the `Table` class.
4.  **Verify:** Run tests (and add new concurrency tests) to ensure the server remains responsive during AI "thinking" time.
