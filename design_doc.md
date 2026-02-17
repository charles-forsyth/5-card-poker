# Design Doc: Betting and Card Drawing

## Overview
Add betting mechanics and a second phase (drawing cards) to the 5-card poker game.

## Architectural Changes

### 1. Data Models (`models.py`)
- `Card`: Remains the same.
- `Hand`: Add a way to identify cards (e.g., index).
- `GameState`:
    - `balance: int` (Player's total money)
    - `current_bet: int` (Amount wagered in current round)
    - `phase: str` (e.g., "betting", "drawing", "result")
    - `held_indices: List[int]`

### 2. Game Logic (`logic.py`)
- `GameLogic` needs to maintain state or we need a way to pass state back and forth.
- `deal(n=5)`: Deals initial hand.
- `draw(hand: List[Card], held_indices: List[int])`: Replaces cards not in `held_indices`.
- `calculate_payout(rank: str, bet: int) -> int`: Returns payout based on hand rank.
    - Royal Flush: 800x
    - Straight Flush: 50x
    - Four of a Kind: 25x
    - Full House: 9x
    - Flush: 6x
    - Straight: 4x
    - Three of a Kind: 3x
    - Two Pair: 2x
    - One Pair (Jacks or Better): 1x (Maybe just One Pair for now)
    - High Card: 0

### 3. API Endpoints (`main.py`)
- `GET /state`: Get current balance and game state.
- `POST /bet`: Place a bet (deduct from balance) and get 5 cards.
- `POST /draw`: Send `held_indices`, get replacement cards, evaluate final hand, update balance.
- `POST /reset`: Reset balance (optional).

### 4. Frontend (`index.html`, `script.js`, `style.css`)
- Display `Balance` and `Bet Amount`.
- Input for `Bet Amount`.
- Cards should be clickable to toggle a `held` class.
- "Deal" button becomes "Draw" after initial deal.

## Workflow
1. Player sets bet and clicks "Deal".
2. 5 cards shown. Phase = "drawing".
3. Player selects cards to hold.
4. Player clicks "Draw".
5. Replacement cards shown. Final hand evaluated. Payout added to balance. Phase = "betting".
