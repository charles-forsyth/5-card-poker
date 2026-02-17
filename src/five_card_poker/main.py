from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .logic import GameLogic
from .models import Hand, GameState

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/five_card_poker/static"), name="static")
templates = Jinja2Templates(directory="src/five_card_poker/templates")

game = GameLogic()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/play")
async def play_hand():
    hand = game.deal()
    return {
        "cards": [{"rank": c.rank.value, "suit": c.suit.value} for c in hand.cards],
        "rank": hand.rank,
        "score": hand.score,
        "deck_count": len(game.deck)
    }

@app.post("/shuffle")
async def shuffle_deck():
    game.shuffle()
    return {"message": "Deck shuffled"}
