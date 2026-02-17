from typing import List
from pydantic import BaseModel
import time
import uuid

class ChatMessage(BaseModel):
    id: str = str(uuid.uuid4())
    player_id: str
    text: str
    timestamp: float = time.time()

class ChatManager:
    def __init__(self):
        self.messages: List[ChatMessage] = []

    def add_message(self, player_id: str, text: str):
        msg = ChatMessage(player_id=player_id, text=text)
        self.messages.append(msg)
        return msg

    def get_messages(self, limit: int = 50):
        return self.messages[-limit:]
