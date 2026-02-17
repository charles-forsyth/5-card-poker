import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .logic import Table, Player, PlayerType
from .models import ActionRequest, DrawRequest, BetRequest, ChatRequest
from .ai import GeminiPokerAgent
from .chat import ChatManager

app = FastAPI()

# Calculate absolute paths for static and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

chat_manager = ChatManager()
table = Table(chat_manager=chat_manager)
table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
# Use different system prompts or persona via distinct agents if desired
agent1 = GeminiPokerAgent(model_name="gemini-2.5-pro")
agent2 = GeminiPokerAgent(model_name="gemini-2.5-pro")

table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI, agent=agent1))
table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI, agent=agent2))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/state")
async def get_state(player_id: str = "player1"):
    return table.to_state(player_id)


@app.post("/action")
async def take_action(request: ActionRequest):
    try:
        amount = request.amount if request.amount is not None else 0
        table.handle_action(request.player_id, request.action, amount)

        # Handle AI turns automatically
        while (
            table.phase in ["betting_1", "betting_2", "drawing"]
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            table.process_ai_turn()

        return table.to_state(request.player_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/draw")
async def draw_cards(request: DrawRequest):
    try:
        player_id = request.player_id or "player1"
        table.handle_draw(player_id, request.held_indices)

        # Handle AI turns automatically
        while (
            table.phase in ["betting_1", "betting_2", "drawing"]
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            table.process_ai_turn()

        return table.to_state(player_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bet")  # Legacy support for Deal button
async def place_bet(request: BetRequest):
    try:
        if request.bet <= 0:
            raise ValueError("Bet must be positive")

        table.start_game(ante=request.bet)
        # Handle AI turns if they are first
        while (
            table.phase in ["betting_1", "betting_2", "drawing"]
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            table.process_ai_turn()

        return table.to_state("player1")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/shuffle")
async def shuffle_deck():
    table.shuffle()
    return {"message": "Deck shuffled"}


@app.post("/reset")
async def reset_game():
    global table, chat_manager
    chat_manager = ChatManager()
    table = Table(chat_manager=chat_manager)
    table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
    agent1 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    agent2 = GeminiPokerAgent(model_name="gemini-2.5-pro")
    table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI, agent=agent1))
    table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI, agent=agent2))
    return {"message": "Game reset"}


@app.post("/chat/send")
async def send_chat_message(request: ChatRequest):
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
                    player_state = player.to_state(hide_hand=False)
                    table_state = table.to_state(player.id)
                    response_text = player.agent.decide_chat_response(
                        request.text, history, player_state, table_state
                    )
                    chat_manager.add_message(player.id, response_text)
                    break  # Only one bot responds per user message

    return msg


@app.get("/chat/messages")
async def get_chat_messages(limit: int = 50):
    return chat_manager.get_messages(limit=limit)


def main():
    uvicorn.run("five_card_poker.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
