from five_card_poker.logic import Table, Player, PlayerType


def test_table_initialization():
    table = Table()
    assert len(table.players) == 0
    assert table.pot == 0
    assert table.phase == "waiting"


def test_add_players():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", type=PlayerType.HUMAN))
    table.add_player(Player(id="p2", name="Bot1", type=PlayerType.AI))
    assert len(table.players) == 2


def test_start_game():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", balance=100))
    table.add_player(Player(id="p2", name="Bot1", balance=100))
    table.start_game(ante=5)

    assert table.pot == 10
    assert table.phase == "betting_1"
    for player in table.players:
        assert len(player.hand.cards) == 5
        assert player.balance == 95


def test_betting_round():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", balance=100))
    table.add_player(Player(id="p2", name="Bot1", balance=100))
    table.start_game(ante=5)  # pot=10, cur_bet=0

    # Alice raises to 10
    table.handle_action("p1", "raise", 10)
    assert table.current_bet == 10
    assert table.players[0].current_bet == 10
    assert table.pot == 20

    # Bot1 calls
    table.handle_action("p2", "call")
    assert table.phase == "drawing"
    assert table.pot == 30
    assert table.current_bet == 0


def test_drawing_round():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", balance=100))
    table.add_player(Player(id="p2", name="Bot1", balance=100))
    table.start_game(ante=5)
    table.handle_action("p1", "call")
    table.handle_action("p2", "call")

    # Alice draws
    old_cards = list(table.players[0].hand.cards)
    table.handle_draw("p1", [0, 1, 2])  # Holds first 3
    assert table.players[0].hand.cards[0] == old_cards[0]
    assert table.players[0].hand.cards[4] != old_cards[4]

    # Bot1 draws (AI automatically)
    table.ai_draw("p2")
    assert table.phase == "betting_2"
