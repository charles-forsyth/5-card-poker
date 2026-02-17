from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logic import Table, Player, PlayerType
from .models import ActionRequest, DrawRequest, BetRequest

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/five_card_poker/static"), name="static")
templates = Jinja2Templates(directory="src/five_card_poker/templates")

table = Table()
table.add_player(Player(id="player1", name="You", type=PlayerType.HUMAN))
table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI))
table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI))


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
            table.phase in ["betting_1", "betting_2"]
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            player = table.players[table.active_player_idx]
            table.handle_action(player.id, "call")

        if (
            table.phase == "drawing"
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            while (
                table.phase == "drawing"
                and table.players[table.active_player_idx].type == PlayerType.AI
            ):
                table.ai_draw(table.players[table.active_player_idx].id)
            # If AI drawing led to betting_2, handle those too
            while (
                table.phase == "betting_2"
                and table.players[table.active_player_idx].type == PlayerType.AI
            ):
                table.handle_action(table.players[table.active_player_idx].id, "call")

        return table.to_state(request.player_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/draw")
async def draw_cards(request: DrawRequest):
    try:
        player_id = request.player_id or "player1"
        table.handle_draw(player_id, request.held_indices)

        # Handle AI drawing turns
        while (
            table.phase == "drawing"
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            table.ai_draw(table.players[table.active_player_idx].id)

        # Handle AI betting turns if we transitioned to betting_2
        while (
            table.phase == "betting_2"
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            table.handle_action(table.players[table.active_player_idx].id, "call")

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
            table.phase in ["betting_1", "betting_2"]
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            player = table.players[table.active_player_idx]
            table.handle_action(player.id, "call")

        # If betting_1 finished immediately (e.g. everyone called), we might be in drawing
        if (
            table.phase == "drawing"
            and table.players[table.active_player_idx].type == PlayerType.AI
        ):
            while (
                table.phase == "drawing"
                and table.players[table.active_player_idx].type == PlayerType.AI
            ):
                table.ai_draw(table.players[table.active_player_idx].id)

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
    table.add_player(Player(id="bot1", name="Bot 1", type=PlayerType.AI))
    table.add_player(Player(id="bot2", name="Bot 2", type=PlayerType.AI))
    return {"message": "Game reset"}
