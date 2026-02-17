import pytest
from fastapi.testclient import TestClient
from five_card_poker.main import app, game
from five_card_poker.logic import GameLogic, Card, Suit, Rank, Hand

client = TestClient(app)

@pytest.fixture
def fresh_game():
    return GameLogic()

def test_deck_creation(fresh_game):
    assert len(fresh_game.deck) == 52

def test_deal_cards(fresh_game):
    hand = fresh_game.deal(5)
    assert len(hand.cards) == 5
    assert len(fresh_game.deck) == 47

def test_evaluate_royal_flush(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.TEN),
        Card(suit=Suit.HEARTS, rank=Rank.JACK),
        Card(suit=Suit.HEARTS, rank=Rank.QUEEN),
        Card(suit=Suit.HEARTS, rank=Rank.KING),
        Card(suit=Suit.HEARTS, rank=Rank.ACE)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Royal Flush"
    assert score == 900

def test_evaluate_straight_flush(fresh_game):
    cards = [
        Card(suit=Suit.SPADES, rank=Rank.NINE),
        Card(suit=Suit.SPADES, rank=Rank.EIGHT),
        Card(suit=Suit.SPADES, rank=Rank.SEVEN),
        Card(suit=Suit.SPADES, rank=Rank.SIX),
        Card(suit=Suit.SPADES, rank=Rank.FIVE)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Straight Flush"
    assert score == 800 + 9 # High card 9

def test_evaluate_four_of_a_kind(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.ACE),
        Card(suit=Suit.DIAMONDS, rank=Rank.ACE),
        Card(suit=Suit.CLUBS, rank=Rank.ACE),
        Card(suit=Suit.SPADES, rank=Rank.ACE),
        Card(suit=Suit.HEARTS, rank=Rank.TWO)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Four of a Kind"
    assert score == 700 + 14

def test_evaluate_full_house(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.KING),
        Card(suit=Suit.DIAMONDS, rank=Rank.KING),
        Card(suit=Suit.CLUBS, rank=Rank.KING),
        Card(suit=Suit.SPADES, rank=Rank.TWO),
        Card(suit=Suit.HEARTS, rank=Rank.TWO)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Full House"
    assert score == 600 + 13

def test_evaluate_flush(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.TWO),
        Card(suit=Suit.HEARTS, rank=Rank.FOUR),
        Card(suit=Suit.HEARTS, rank=Rank.SIX),
        Card(suit=Suit.HEARTS, rank=Rank.EIGHT),
        Card(suit=Suit.HEARTS, rank=Rank.TEN)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Flush"
    assert score == 500 + 10 # High card 10

def test_evaluate_straight(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.TWO),
        Card(suit=Suit.DIAMONDS, rank=Rank.THREE),
        Card(suit=Suit.CLUBS, rank=Rank.FOUR),
        Card(suit=Suit.SPADES, rank=Rank.FIVE),
        Card(suit=Suit.HEARTS, rank=Rank.SIX)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Straight"
    assert score == 400 + 6 # High card 6

def test_evaluate_wheel_straight(fresh_game):
    cards = [
        Card(suit=Suit.HEARTS, rank=Rank.ACE),
        Card(suit=Suit.DIAMONDS, rank=Rank.TWO),
        Card(suit=Suit.CLUBS, rank=Rank.THREE),
        Card(suit=Suit.SPADES, rank=Rank.FOUR),
        Card(suit=Suit.HEARTS, rank=Rank.FIVE)
    ]
    score, rank_name = fresh_game.evaluate_hand(cards)
    assert rank_name == "Straight"
    # Wheel is 5-high straight. My logic returns 400 + 5.
    # In my logic: values = [5, 4, 3, 2, 1] -> high card 5.
    assert score == 400 + 5

def test_api_play():
    response = client.get("/play")
    assert response.status_code == 200
    data = response.json()
    assert "cards" in data
    assert len(data["cards"]) == 5
    assert "rank" in data
    assert "score" in data
    assert "deck_count" in data

def test_api_shuffle():
    response = client.post("/shuffle")
    assert response.status_code == 200
    assert response.json() == {"message": "Deck shuffled"}
