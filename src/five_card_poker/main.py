from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logic import GameLogic

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/five_card_poker/static"), name="static")
templates = Jinja2Templates(directory="src/five_card_poker/templates")

game = GameLogic()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/state")
async def get_state():
    return {
        "balance": game.balance,
        "current_bet": game.current_bet,
        "phase": game.phase,
        "cards": [
            {"rank": c.rank.value, "suit": c.suit.value}
            for c in game.current_hand.cards
        ]
        if game.current_hand
        else [],
        "rank": game.current_hand.rank if game.current_hand else "Waiting to Deal",
        "score": game.current_hand.score if game.current_hand else 0,
        "deck_count": len(game.deck),
    }


@app.post("/bet")
async def place_bet(request: Request):
    data = await request.json()
    bet = data.get("bet", 1)
    try:
        hand = game.deal(bet)
        return {
            "cards": [{"rank": c.rank.value, "suit": c.suit.value} for c in hand.cards],
            "rank": hand.rank,
            "score": hand.score,
            "balance": game.balance,
            "deck_count": len(game.deck),
            "phase": game.phase,
        }
    except ValueError as e:
        return {"error": str(e)}, 400


@app.post("/draw")
async def draw_cards(request: Request):
    data = await request.json()
    held_indices = data.get("held_indices", [])
    try:
        hand = game.draw(held_indices)
        return {
            "cards": [{"rank": c.rank.value, "suit": c.suit.value} for c in hand.cards],
            "rank": hand.rank,
            "score": hand.score,
            "balance": game.balance,
            "deck_count": len(game.deck),
            "phase": game.phase,
        }
    except ValueError as e:
        return {"error": str(e)}, 400


@app.post("/shuffle")
async def shuffle_deck():
    game.shuffle()
    return {"message": "Deck shuffled", "deck_count": len(game.deck)}
