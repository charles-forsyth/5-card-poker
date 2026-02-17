from fastapi.testclient import TestClient
from five_card_poker.main import app
from five_card_poker.logic import Table, Player, PlayerType
from five_card_poker.chat import ChatManager

client = TestClient(app)


def test_chat_manager_add_message():
    manager = ChatManager()
    msg = manager.add_message("player1", "Hello")
    assert msg.player_id == "player1"
    assert msg.text == "Hello"
    assert len(manager.messages) == 1


def test_chat_manager_get_messages():
    manager = ChatManager()
    manager.add_message("p1", "Msg 1")
    manager.add_message("p2", "Msg 2")
    msgs = manager.get_messages()
    assert len(msgs) == 2
    assert msgs[0].text == "Msg 1"
    assert msgs[1].text == "Msg 2"


def test_table_logs_events():
    # Setup table with chat manager
    chat_manager = ChatManager()
    table = Table(chat_manager=chat_manager)
    p1 = Player("p1", "Player 1", PlayerType.HUMAN, balance=100)
    p2 = Player("p2", "Player 2", PlayerType.HUMAN, balance=100)
    table.add_player(p1)
    table.add_player(p2)

    # Start game (should log "Game started")
    table.start_game(ante=5)
    assert len(chat_manager.messages) > 0
    message_texts = [msg.text.lower() for msg in chat_manager.messages]
    assert any("started" in t or "ante" in t for t in message_texts)

    # Action (should log "Player 1 checks/bets/etc")
    # p2 is dealer, p1 is active first
    table.handle_action("p1", "call")
    # Check last few messages
    recent_texts = [msg.text.lower() for msg in chat_manager.messages[-2:]]
    assert any("call" in t for t in recent_texts)


def test_api_chat_send():
    response = client.post(
        "/chat/send", json={"player_id": "player1", "text": "Hello World"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Hello World"
    assert data["player_id"] == "player1"


def test_api_chat_get():

    # Send a message first

    client.post("/chat/send", json={"player_id": "player1", "text": "Test Get"})

    response = client.get("/chat/messages")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    # Check if our message is in the last two (in case a bot replied)

    message_texts = [msg["text"] for msg in data[-2:]]

    assert "Test Get" in message_texts
