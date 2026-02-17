# 5 Card Poker Web App

A modern 5-card poker web application built with FastAPI and vanilla JavaScript.

## Features
- Classic 5-card draw poker logic.
- Dark mode UI.
- Real-time balance and game state management.
- Robust API validation using Pydantic.

## Stability Improvements (v0.2.1)
- **Input Validation:** All API endpoints now use Pydantic models for strict type checking and validation.
- **Phase Enforcement:** Game transitions (betting -> drawing) are strictly enforced in the backend.
- **Error Handling:** Improved error responses using FastAPI's `HTTPException`.
- **Reset Functionality:** New `/reset` endpoint to restart the game state.
- **Testing:** Expanded test suite covering edge cases and invalid inputs.

## Getting Started
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Run the application:
   ```bash
   uv run uvicorn src.five_card_poker.main:app --reload
   ```

## Development
Run tests and quality checks:
```bash
uv run pytest
uv run ruff check .
uv run mypy src
```
