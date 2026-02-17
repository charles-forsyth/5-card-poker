# 🃏 5-Card Draw Poker: AI-Enhanced Edition

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.5-green.svg)](https://github.com/chuck/5-card-poker)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/AI-Gemini_2.5_Pro-blue.svg?logo=google-gemini)](https://deepmind.google/technologies/gemini/)

A high-performance, asynchronous 5-card draw poker web application. This project combines a modern **FastAPI** backend with **Google Gemini 2.5 Pro** powered AI opponents that not only play the game but also engage in context-aware trash talk.

---

## ✨ Key Features

- **🤖 Advanced AI Players:** Powered by `gemini-2.5-pro`, AI opponents make strategic betting and drawing decisions based on the game state.
- **💬 Contextual AI Chat:** AI players react to game events and user messages with a professional poker persona.
- **⚡ Asynchronous Architecture:** Fully `async/await` backend for high-performance game logic and AI interactions.
- **🎨 Modern Dark-Mode UI:** A sleek, responsive frontend built with vanilla JavaScript and CSS variables.
- **🛡️ Robust Validation:** Pydantic-powered schemas ensure game state integrity and API safety.
- **🏗️ Skywalker Workflow:** Developed using professional-grade CI/CD and automated quality gauntlets.

---

## 🚀 Quick Start

### Prerequisites
- [uv](https://github.com/astral-sh/uv) - The lightning-fast Python package manager.
- A `GEMINI_API_KEY` (Optional, fallbacks to rule-based logic).

### Installation & Launch

1. **Clone and Install:**
   ```bash
   git clone https://github.com/chuck/5-card-poker.git
   cd 5-card-poker
   uv sync
   ```

2. **Set Environment Variables:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

3. **Run the App:**
   ```bash
   uv run five-card-poker
   ```
   *Visit `http://localhost:8080` to start playing!*

---

## 🧠 AI Integration

The `GeminiPokerAgent` leverages LLMs for three core game mechanics:

1.  **Strategic Betting:** Analyzes hand strength, pot size, and opponent behavior to decide between `check`, `call`, `raise`, or `fold`.
2.  **Optimal Drawing:** Decides which cards to hold or discard during the draw phase to maximize hand potential.
3.  **Persona Chat:** Generates short, personality-driven messages responding to real-time game history.

---

## 🛠️ Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Frontend:** HTML5, CSS3 (Modern Dark Mode), Vanilla JavaScript
- **AI Engine:** [Google GenAI (Gemini)](https://ai.google.dev/)
- **Packaging:** [uv](https://astral-sh.com/uv), [Hatchling](https://hatch.pypa.io/)
- **Quality Assurance:** [Pytest](https://pytest.org/), [Ruff](https://beta.ruff.rs/), [Mypy](https://mypy-lang.org/)

---

## 📁 Project Structure

```text
src/five_card_poker/
├── ai.py           # Gemini AI Agent logic
├── chat.py         # Chat management and history
├── logic.py        # Core Poker game mechanics & rules
├── main.py         # FastAPI application and endpoints
├── models.py       # Pydantic state models and schemas
├── static/         # Frontend assets (JS, CSS)
└── templates/      # HTML templates (Jinja2)
```

---

## 🛡️ Skywalker Development Workflow

This project adheres to the **Skywalker Development Workflow**, ensuring peak code quality and reliability:

1.  **Branch & Bump:** Feature-specific branches and semantic versioning.
2.  **The Local Gauntlet:**
    - `uv run ruff check . --fix` (Linting)
    - `uv run ruff format .` (Formatting)
    - `uv run mypy src` (Type Checking)
    - `uv run pytest` (Unit & Integration Testing)
3.  **PR & CI/CD:** Automated checks and peer review via GitHub Actions.
4.  **Release:** Semantic tagging and automated deployment.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

*Built with ❤️ by [Chuck Forsyth](mailto:forsythc@ucr.edu)*
