from enum import Enum
from pydantic import BaseModel
from typing import List


class Suit(str, Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


class Card(BaseModel):
    suit: Suit
    rank: Rank

    def __str__(self):
        return f"{self.rank.value} of {self.suit.value}"


class Hand(BaseModel):
    cards: List[Card]
    rank: str  # e.g., "Full House", "Flush", etc.
    score: int  # For comparison


class GameState(BaseModel):
    player_hand: Hand
    deck_count: int
    balance: int = 100
    current_bet: int = 0
    phase: str = "betting"  # betting, drawing, result
    message: str = ""


class BetRequest(BaseModel):
    bet: int


class DrawRequest(BaseModel):
    held_indices: List[int]
