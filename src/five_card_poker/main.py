from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logic import GameLogic
from .models import BetRequest, DrawRequest

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
async def place_bet(request: BetRequest):
    try:
        hand = game.deal(request.bet)
        return {
            "cards": [{"rank": c.rank.value, "suit": c.suit.value} for c in hand.cards],
            "rank": hand.rank,
            "score": hand.score,
            "balance": game.balance,
            "deck_count": len(game.deck),
            "phase": game.phase,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/draw")
async def draw_cards(request: DrawRequest):
    try:
        hand = game.draw(request.held_indices)
        return {
            "cards": [{"rank": c.rank.value, "suit": c.suit.value} for c in hand.cards],
            "rank": hand.rank,
            "score": hand.score,
            "balance": game.balance,
            "deck_count": len(game.deck),
            "phase": game.phase,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/shuffle")
async def shuffle_deck():
    game.shuffle()
    return {"message": "Deck shuffled", "deck_count": len(game.deck)}


@app.post("/reset")
async def reset_game():
    game.reset()
    return {"message": "Game reset", "balance": game.balance, "phase": game.phase}
