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


def test_autoplay_toggle():
    table = Table()
    player1 = Player(id="player1", name="You", type=PlayerType.HUMAN)
    table.add_player(player1)

    # Toggle on
    is_active = table.toggle_autoplay()
    assert is_active is True
    assert table.autoplay is True
    assert player1.type == PlayerType.AI
    assert player1.agent is not None
    assert player1.agent.model_name == "gemini-3.1-flash"

    # Toggle off
    is_active = table.toggle_autoplay()
    assert is_active is False
    assert table.autoplay is False
    assert player1.type == PlayerType.HUMAN
    assert player1.agent is None


def test_autoplay_spectator_cards_reveal():
    table = Table()
    p1 = Player(id="player1", name="You", type=PlayerType.HUMAN, balance=100)
    p2 = Player(id="bot1", name="Rhiannon", type=PlayerType.AI, balance=100)
    table.add_player(p1)
    table.add_player(p2)

    table.toggle_autoplay()  # Turn on autoplay
    table.start_game(ante=5)

    # From Player1 (Human/Spectator) perspective:
    state_p1 = table.to_state("player1")
    assert state_p1.autoplay is True
    # Opponents' hand MUST be revealed to the spectator!
    opp_state = next(p for p in state_p1.players if p.id == "bot1")
    assert opp_state.hand is not None

    # From Bot1 (AI opponent) perspective:
    state_bot1 = table.to_state("bot1")
    # Opponents' hands (player1) MUST be hidden from the AI to prevent cheating!
    p1_state_from_bot = next(p for p in state_bot1.players if p.id == "player1")
    assert p1_state_from_bot.hand is None


def test_autoplay_chips_replenish():
    table = Table()
    p1 = Player(id="player1", name="You", type=PlayerType.HUMAN, balance=2)
    p2 = Player(id="bot1", name="Rhiannon", type=PlayerType.AI, balance=100)
    table.add_player(p1)
    table.add_player(p2)

    table.toggle_autoplay()  # Turn on autoplay
    table.start_game(ante=10)

    # Check that Player1's balance was automatically replenished to 100 and ante was deducted
    assert p1.balance == 90
    assert p1.is_active is True
