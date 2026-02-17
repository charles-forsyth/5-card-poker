from five_card_poker.logic import Table, Player, PlayerType


def test_ai_turn_after_human_check():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", type=PlayerType.HUMAN, balance=100))
    table.add_player(Player(id="p2", name="Bot1", type=PlayerType.AI, balance=100))

    # Alice is dealer (idx 0), Bot1 acts first (idx 1)
    table.dealer_idx = 0
    table.start_game(ante=5)

    # Currently Bot1 is active. Let's make it Alice's turn to simulate the bug better.
    # Actually, in start_game, active_player_idx is set to (dealer_idx + 1) % len.
    # So Bot1 is indeed first.
    assert table.players[table.active_player_idx].id == "p2"

    # If Alice was first (e.g. Bot1 is dealer)
    table = Table()
    table.add_player(Player(id="p1", name="Alice", type=PlayerType.HUMAN, balance=100))
    table.add_player(Player(id="p2", name="Bot1", type=PlayerType.AI, balance=100))
    table.dealer_idx = 1  # Bot1 is dealer
    table.start_game(ante=5)

    assert table.active_player_idx == 0  # Alice's turn

    # Alice checks
    table.handle_action("p1", "check")

    # EXPECTATION: It should be Bot1's turn, NOT the drawing phase yet.
    assert table.phase == "betting_1"
    assert table.players[table.active_player_idx].id == "p2"


def test_ai_turn_after_human_raise():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", type=PlayerType.HUMAN, balance=100))
    table.add_player(Player(id="p2", name="Bot1", type=PlayerType.AI, balance=100))
    table.dealer_idx = 1
    table.start_game(ante=5)

    # Alice raises
    table.handle_action("p1", "raise", 10)

    # It should be Bot1's turn
    assert table.phase == "betting_1"
    assert table.players[table.active_player_idx].id == "p2"
