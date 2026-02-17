from five_card_poker.logic import Table, Player


def test_draw_advances_phase():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", balance=100))
    # No other players for simplicity
    table.start_game(ante=5)

    # Skip betting_1
    table.phase = "drawing"
    table.active_player_idx = 0

    # Alice draws
    table.handle_draw("p1", [0, 1, 2, 3, 4])

    # Phase should now be betting_2 because Alice was the only player
    assert table.phase == "betting_2"


def test_draw_advances_turn():
    table = Table()
    table.add_player(Player(id="p1", name="Alice", balance=100))
    table.add_player(Player(id="p2", name="Bob", balance=100))
    table.start_game(ante=5)

    table.phase = "drawing"
    table.active_player_idx = 0

    # Alice draws
    table.handle_draw("p1", [0, 1, 2, 3, 4])

    # Phase should still be drawing
    assert table.phase == "drawing"
    # Active player should be Bob (index 1)
    assert table.active_player_idx == 1

    # Bob draws
    table.handle_draw("p2", [0, 1, 2, 3, 4])

    # Now phase should be betting_2
    assert table.phase == "betting_2"
