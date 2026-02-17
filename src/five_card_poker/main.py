from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logic import Table, Player, PlayerType
from .models import ActionRequest, DrawRequest, BetRequest
from .ai import GeminiPokerAgent

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/five_card_poker/static"), name="static")
templates = Jinja2Templates(directory="src/five_card_poker/templates")

table = Table()
table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
# Use different system prompts or persona via distinct agents if desired
agent1 = GeminiPokerAgent(model_name="gemini-2.5-flash")
agent2 = GeminiPokerAgent(model_name="gemini-2.5-flash")

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
    global table
    table = Table()
    table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
    agent1 = GeminiPokerAgent(model_name="gemini-2.5-flash")
    agent2 = GeminiPokerAgent(model_name="gemini-2.5-flash")
    table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI, agent=agent1))
    table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI, agent=agent2))
    return {"message": "Game reset"}
