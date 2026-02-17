import random
from collections import Counter
from .models import Card, Suit, Rank, Hand, GameState

class GameLogic:
    def __init__(self):
        self.deck = self._create_deck()
        self.shuffle()

    def _create_deck(self):
        return [Card(suit=s, rank=r) for s in Suit for r in Rank]

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self, n=5) -> Hand:
        if len(self.deck) < n:
            self.deck = self._create_deck()
            self.shuffle()
        
        cards = [self.deck.pop() for _ in range(n)]
        score, rank_name = self.evaluate_hand(cards)
        return Hand(cards=cards, rank=rank_name, score=score)

    @staticmethod
    def _rank_value(rank: Rank) -> int:
        mapping = {
            Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4, Rank.FIVE: 5,
            Rank.SIX: 6, Rank.SEVEN: 7, Rank.EIGHT: 8, Rank.NINE: 9,
            Rank.TEN: 10, Rank.JACK: 11, Rank.QUEEN: 12, Rank.KING: 13,
            Rank.ACE: 14
        }
        return mapping[rank]

    def evaluate_hand(self, cards: list[Card]) -> tuple[int, str]:
        if len(cards) != 5:
            return 0, "Invalid Hand"

        values = sorted([self._rank_value(c.rank) for c in cards], reverse=True)
        suits = [c.suit for c in cards]
        counts = Counter(values)
        sorted_counts = counts.most_common() # [(value, count), ...]

        is_flush = len(set(suits)) == 1
        
        # Check straight
        is_straight = False
        if len(set(values)) == 5:
            if values[0] - values[4] == 4:
                is_straight = True
            # Check A-5 straight (Wheel)
            if set(values) == {14, 5, 4, 3, 2}:
                is_straight = True
                values = [5, 4, 3, 2, 1] # Treat Ace as low

        # Royal Flush
        if is_flush and is_straight and set(values) == {14, 13, 12, 11, 10}:
            return 900, "Royal Flush"
        
        # Straight Flush
        if is_flush and is_straight:
            return 800 + values[0], "Straight Flush"
        
        # Four of a Kind
        if sorted_counts[0][1] == 4:
            return 700 + sorted_counts[0][0], "Four of a Kind"
        
        # Full House
        if sorted_counts[0][1] == 3 and sorted_counts[1][1] == 2:
            return 600 + sorted_counts[0][0], "Full House"
        
        # Flush
        if is_flush:
            return 500 + values[0], "Flush"
        
        # Straight
        if is_straight:
            return 400 + values[0], "Straight"
        
        # Three of a Kind
        if sorted_counts[0][1] == 3:
            return 300 + sorted_counts[0][0], "Three of a Kind"
        
        # Two Pair
        if sorted_counts[0][1] == 2 and sorted_counts[1][1] == 2:
            return 200 + max(sorted_counts[0][0], sorted_counts[1][0]), "Two Pair"
        
        # One Pair
        if sorted_counts[0][1] == 2:
            return 100 + sorted_counts[0][0], "One Pair"
        
        # High Card
        return values[0], "High Card"
