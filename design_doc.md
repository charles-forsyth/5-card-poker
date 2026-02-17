# Design Doc: Stability and Performance Improvements

## Overview
This document outlines the plan to improve the stability and performance of the 5-card poker application. Key areas include thread safety, asynchronous AI interactions, and hand evaluation optimization.

## Proposed Changes

### 1. Asynchronous AI Operations
Current AI calls (`decide_draw_action`, `decide_betting_action`, `decide_chat_response`) are synchronous and potentially block the FastAPI event loop during network I/O.
- **Change:** Refactor `GeminiPokerAgent` methods to be `async`.
- **Change:** Update `Table.process_ai_turn` and chat endpoints to use `await`.

### 2. Thread Safety and Concurrency
The `Table` and `ChatManager` instances are global and modified by synchronous requests.
- **Change:** Use an `asyncio.Lock` to protect access to the `Table` state during transitions.
- **Change:** Ensure all state modifications are atomic within the lock context.

### 3. Hand Evaluation Optimization
`evaluate_hand` uses `Counter` and multiple list operations.
- **Change:** Implement a more efficient evaluation algorithm if possible, or at least minimize redundant calculations.
- **Change:** Cache evaluation results for the same set of cards within a `Hand` object.

### 4. Logging and Monitoring
- **Change:** Integrate Python's `logging` module to track game state transitions and errors.
- **Change:** Log AI response times and failures.

### 5. Dependency Injection
- **Change:** Move `Table` and `ChatManager` instantiation into a dependency that FastAPI can inject, making it easier to test and manage lifecycle.

## Implementation Details

### src/five_card_poker/ai.py
- Make methods `async`.
- Use `asyncio.to_thread` for non-async library calls if necessary, or use an async client if available.

### src/five_card_poker/logic.py
- Add `asyncio.Lock`.
- Update methods to be `async` where they interact with AI.

### src/five_card_poker/main.py
- Use `app.state` to store `Table` and `ChatManager`.
- Update endpoints to be fully `async`.

## Verification Plan
- **Unit Tests:** Verify `evaluate_hand` with all poker hand types.
- **Integration Tests:** Test the `async` flow of AI turns.
- **Load Tests:** Simulate multiple concurrent users to ensure no race conditions.
