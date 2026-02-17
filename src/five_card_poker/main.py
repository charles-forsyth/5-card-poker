import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .logic import Table, Player, PlayerType
from .models import ActionRequest, DrawRequest, BetRequest, ChatRequest
from .ai import GeminiPokerAgent
from .chat import ChatManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Calculate absolute paths for static and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_manager = ChatManager()
    table = Table(chat_manager=chat_manager)
    table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
    agent1 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    agent2 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI, agent=agent1))
    table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI, agent=agent2))

    app.state.table = table
    app.state.chat_manager = chat_manager
    logger.info("Game state initialized")
    yield
    # Clean up if needed
    logger.info("Shutting down")


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


async def get_table() -> Table:
    return app.state.table


async def get_chat_manager() -> ChatManager:
    return app.state.chat_manager


async def run_ai_turns(table: Table):
    """
    Background task to process AI turns sequentially.
    """
    try:
        while True:
            # Check if game is in a phase where players act
            if table.phase not in ["betting_1", "betting_2", "drawing"]:
                break

            # Check if active player is AI
            current_player = table.players[table.active_player_idx]
            if current_player.type != PlayerType.AI:
                break

            # Process the turn
            # process_ai_turn in logic.py is async and handles:
            # 1. Getting state
            # 2. Calling AI (yields)
            # 3. Handling action (sync)
            await table.process_ai_turn()

            # Small pause to allow other tasks (like state polling) to run effectively
            await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in AI background loop: {e}", exc_info=True)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/state")
async def get_state(player_id: str = "player1", table: Table = Depends(get_table)):
    # We acquire lock to ensure we don't read partial updates if handle_action runs?
    # handle_action is sync, so it's atomic in asyncio.
    # But lock usage is good practice if we expand to threads.
    async with table._lock:
        return table.to_state(player_id)


@app.post("/action")
async def take_action(
    request: ActionRequest,
    background_tasks: BackgroundTasks,
    table: Table = Depends(get_table),
):
    async with table._lock:
        try:
            amount = request.amount if request.amount is not None else 0
            table.handle_action(request.player_id, request.action, amount)
        except ValueError as e:
            logger.error(f"Action error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Check if AI turn follows
    current_player = table.players[table.active_player_idx]
    if (
        current_player.type == PlayerType.AI
        and table.phase in ["betting_1", "betting_2", "drawing"]
    ):
        background_tasks.add_task(run_ai_turns, table)

    return table.to_state(request.player_id)


@app.post("/draw")
async def draw_cards(
    request: DrawRequest,
    background_tasks: BackgroundTasks,
    table: Table = Depends(get_table),
):
    async with table._lock:
        try:
            player_id = request.player_id or "player1"
            table.handle_draw(player_id, request.held_indices)
        except ValueError as e:
            logger.error(f"Draw error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Check if AI turn follows
    current_player = table.players[table.active_player_idx]
    if (
        current_player.type == PlayerType.AI
        and table.phase in ["betting_1", "betting_2", "drawing"]
    ):
        background_tasks.add_task(run_ai_turns, table)

    return table.to_state(player_id)


@app.post("/bet")  # Legacy support for Deal button
async def place_bet(
    request: BetRequest,
    background_tasks: BackgroundTasks,
    table: Table = Depends(get_table),
):
    async with table._lock:
        try:
            if request.bet <= 0:
                raise ValueError("Bet must be positive")

            table.start_game(ante=request.bet)
        except ValueError as e:
            logger.error(f"Bet error: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    # Check if AI turn follows (e.g. if dealer button makes AI first)
    current_player = table.players[table.active_player_idx]
    if (
        current_player.type == PlayerType.AI
        and table.phase in ["betting_1", "betting_2", "drawing"]
    ):
        background_tasks.add_task(run_ai_turns, table)

    return table.to_state("player1")


@app.post("/shuffle")
async def shuffle_deck(table: Table = Depends(get_table)):
    async with table._lock:
        table.shuffle()
        return {"message": "Deck shuffled"}


@app.post("/reset")
async def reset_game():
    chat_manager = ChatManager()
    table = Table(chat_manager=chat_manager)
    table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
    agent1 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    agent2 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI, agent=agent1))
    table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI, agent=agent2))

    app.state.table = table
    app.state.chat_manager = chat_manager
    return {"message": "Game reset"}


@app.post("/chat/send")
async def send_chat_message(
    request: ChatRequest,
    table: Table = Depends(get_table),
    chat_manager: ChatManager = Depends(get_chat_manager),
):
    msg = chat_manager.add_message(request.player_id, request.text)

    # Trigger bot responses
    if request.player_id == "player1":
        # Get history for context
        history = [m.text for m in chat_manager.get_messages(limit=10)]

        # Pick a bot to respond (or all)
        for player in table.players:
            if player.type == PlayerType.AI and player.agent:
                # 50% chance for a bot to respond to keep it from being too noisy
                import random

                if random.random() < 0.5:
                    async with table._lock:
                        player_state = player.to_state(hide_hand=False)
                        table_state = table.to_state(player.id)

                    response_text = await player.agent.decide_chat_response(
                        request.text, history, player_state, table_state
                    )
                    chat_manager.add_message(player.id, response_text)
                    break  # Only one bot responds per user message

    return msg


@app.get("/chat/messages")
async def get_chat_messages(
    limit: int = 50, chat_manager: ChatManager = Depends(get_chat_manager)
):
    return chat_manager.get_messages(limit=limit)


def main():
    uvicorn.run("five_card_poker.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
