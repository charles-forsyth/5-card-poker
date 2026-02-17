from five_card_poker.logic import GameLogic
from five_card_poker.models import Card, Suit, Rank, Hand


def test_calculate_payout():
    logic = GameLogic()
    assert logic.calculate_payout("Royal Flush", 10) == 8000
    assert logic.calculate_payout("Straight Flush", 10) == 500
    assert logic.calculate_payout("Four of a Kind", 10) == 250
    assert logic.calculate_payout("Full House", 10) == 90
    assert logic.calculate_payout("Flush", 10) == 60
    assert logic.calculate_payout("Straight", 10) == 40
    assert logic.calculate_payout("Three of a Kind", 10) == 30
    assert logic.calculate_payout("Two Pair", 10) == 20
    assert logic.calculate_payout("One Pair", 10) == 10
    assert logic.calculate_payout("High Card", 10) == 0


def test_draw_cards():
    logic = GameLogic()
    initial_cards = [
        Card(suit=Suit.HEARTS, rank=Rank.ACE),
        Card(suit=Suit.DIAMONDS, rank=Rank.ACE),
        Card(suit=Suit.CLUBS, rank=Rank.TWO),
        Card(suit=Suit.SPADES, rank=Rank.THREE),
        Card(suit=Suit.HEARTS, rank=Rank.FOUR),
    ]
    # Manually set state for test
    logic.current_hand = Hand(cards=initial_cards, rank="One Pair", score=114)
    logic.phase = "drawing"
    logic.current_bet = 10

    # Hold the two Aces (indices 0 and 1)
    held_indices = [0, 1]
    final_hand = logic.draw(held_indices)
    new_cards = final_hand.cards

    assert len(new_cards) == 5
    assert new_cards[0] == initial_cards[0]
    assert new_cards[1] == initial_cards[1]
    assert new_cards[2] != initial_cards[2]
    assert new_cards[3] != initial_cards[3]
    assert new_cards[4] != initial_cards[4]


def test_draw_all_cards():
    logic = GameLogic()
    logic.deal(10)
    initial_cards = list(logic.current_hand.cards)
    final_hand = logic.draw([])
    new_cards = final_hand.cards
    assert len(new_cards) == 5
    for i in range(5):
        assert new_cards[i] not in initial_cards


def test_draw_no_cards():
    logic = GameLogic()
    logic.deal(10)
    initial_cards = list(logic.current_hand.cards)
    final_hand = logic.draw([0, 1, 2, 3, 4])
    new_cards = final_hand.cards
    assert new_cards == initial_cards
