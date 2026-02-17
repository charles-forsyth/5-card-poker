import json
import os
import google.generativeai as genai
from typing import List, Tuple, Optional
from .models import PlayerState, TableState, Hand


class GeminiPokerAgent:
    def __init__(
        self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            # In a real app we might raise error, but here let's warn or handle gracefully?
            # For now, let's assume it's provided or mocked.
            pass
        else:
            genai.configure(api_key=self.api_key)

        self.model = genai.GenerativeModel(model_name)

    def _format_hand(self, hand: Optional[Hand]) -> str:
        if not hand:
            return "Unknown"
        return ", ".join([str(c) for c in hand.cards])

    def decide_betting_action(
        self, player_state: PlayerState, table_state: TableState
    ) -> Tuple[str, int]:
        hand_str = self._format_hand(player_state.hand)
        prompt = f"""
        You are playing 5-Card Draw Poker.
        Your hand: {hand_str} ({player_state.hand.rank if player_state.hand else "Unknown"}).
        Your balance: {player_state.balance}.
        Current Pot: {table_state.pot}.
        Current Bet to Match: {table_state.current_bet}.
        Your Current Bet: {player_state.current_bet}.
        Phase: {table_state.phase}.
        
        Decide your action:
        - "fold": Give up.
        - "call": Match the current bet.
        - "raise": Increase the bet (must be > current bet).
        - "check": Pass if current bet is equal to your bet.
        
        Respond ONLY with a JSON object:
        {{
            "action": "call" | "fold" | "raise" | "check",
            "amount": <integer> (0 for fold/check/call, raise amount for raise)
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # Cleanup JSON block if present
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()

            data = json.loads(text)
            return data.get("action", "fold"), data.get("amount", 0)
        except Exception as e:
            print(f"Gemini Error: {e}")
            return "fold", 0

    def decide_draw_action(
        self, player_state: PlayerState, table_state: TableState
    ) -> List[int]:
        hand_str = self._format_hand(player_state.hand)
        prompt = f"""
        You are playing 5-Card Draw Poker. It is the Draw phase.
        Your hand: {hand_str} ({player_state.hand.rank if player_state.hand else "Unknown"}).
        
        Decide which cards to HOLD (keep). The rest will be discarded and replaced.
        Indices are 0-4 corresponding to the cards in your hand.
        
        Respond ONLY with a JSON object:
        {{
            "held_indices": [0, 1, ...]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # Cleanup JSON block if present
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()

            data = json.loads(text)
            return data.get("held_indices", [])
        except Exception as e:
            print(f"Gemini Error: {e}")
            return []
