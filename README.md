# 🔮 Witching Hour Poker 🔮 (v0.5.0)

A modern, high-fidelity, high-immersive 5-card draw poker web application themed around an Earth Nature & Witchy aesthetic, built with FastAPI, vanilla CSS/JS, and Google's Gemini models.

## 🌙 Features & Witchcraft
- **Premium Earth Nature / Witchy Theme:** A stunning, animated, responsive visual overhaul featuring floating mystical mist, a glowing central cauldron, parchment grimoire cards, and golden runic active state auras.
- **6-Player Coven Mode:** Play against 5 distinct AI coven members (*Rhiannon, Althea, Zephyr, Madrigal, and Morrigan*) powered by `gemini-3.1-pro`.
- **Procedural Sound Synthesis (Web Audio API):** Direct browser sound synthesis with zero external audio assets! Immersive sounds include cascading parchment card deals, glistening wind chimes, bubbling cauldron potion pops, fire-frizzling card folds, and resonant spell-charging raises.
- **Real-Time Coven Whispering Chat:** A built-in chat panel displaying live bot communication, real-time thoughts, and a central state journal.
- **Moonlight Mode Toggles:** Switch between the deep-forest "Witchy Night" and "Moonlight" theme on demand.
- **🔮 Oracle Mode (AI Autoplay):** Toggle a premium autoplay mode where your grimoire is controlled by **Gemini 3.1 Flash**. In Oracle Mode, player cards are fully revealed to you (the spectator), while remain hidden from other AI coven members to prevent cheating. Game turns progress step-by-step with natural procedural delays, and new hands are automatically initiated at showdown with crystals replenished to $100 for bankrupt coven players.

## 🔮 Stability & Architectural Improvements (v0.5.0)
- **Zero-Dependency sound system:** Using the browser's built-in `AudioContext` ensuring it's extremely lightweight, instantaneous, and immune to broken link errors.
- **Full Skywalker Development Workflow integration:** Fully vetted under Ruff, formatted, and strictly typed under Mypy.
- **Oracle Mode Spectacle Engine:** Auto-runs the entire match loop with automated step requests, card selection blockades, and secure server-side spectator state projection.
- **Expanded Multiplayer Engine:** Vetted and 100% green against all 47 unit and integration tests under `pytest`.

## Getting Started
1. Install dependencies and sync your lockfile:
   ```bash
   uv sync
   ```
2. Run the application:
   ```bash
   uv run uvicorn src.five_card_poker.main:app --reload
   ```

## Development
Run tests, linter, formatting, and type checks to pass the Local Gauntlet:
```bash
uv run ruff check . --fix
uv run ruff format .
uv run mypy src
uv run pytest
```
