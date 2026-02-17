import json
import os
import logging
from google import genai
from typing import List, Tuple, Optional
from .models import PlayerState, TableState, Hand

logger = logging.getLogger(__name__)


class GeminiPokerAgent:
    def __init__(
        self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-pro"
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning(
                "No API key found for GeminiPokerAgent. Falling back to rule-based logic."
            )

    def _format_hand(self, hand: Optional[Hand]) -> str:
        if not hand:
            return "Unknown"
        return ", ".join([str(c) for c in hand.cards])

    def _rule_based_betting(
        self, player_state: PlayerState, table_state: TableState
    ) -> Tuple[str, int]:
        """Simple rule-based fallback for betting."""
        if not player_state.hand:
            return "fold", 0

        # If we have a pair or better, call. Otherwise fold if bet is high.
        if player_state.hand.score >= 100:  # One Pair or better
            if table_state.current_bet > player_state.current_bet:
                return "call", 0
            else:
                return "check", 0

        if table_state.current_bet == player_state.current_bet:
            return "check", 0

        return "fold", 0

    def _rule_based_draw(self, player_state: PlayerState) -> List[int]:
        """Simple rule-based fallback for drawing."""
        if not player_state.hand:
            return [0, 1, 2, 3, 4]

        from collections import Counter

        # Keep pairs or better
        ranks = [c.rank for c in player_state.hand.cards]
        counts = Counter(ranks)
        held = [i for i, c in enumerate(player_state.hand.cards) if counts[c.rank] >= 2]
        return held

    async def decide_betting_action(
        self, player_state: PlayerState, table_state: TableState
    ) -> Tuple[str, int]:
        if not self.client:
            return self._rule_based_betting(player_state, table_state)

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
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            if response.text:
                data = json.loads(response.text)
                return data.get("action", "fold"), data.get("amount", 0)
            else:
                return self._rule_based_betting(player_state, table_state)
        except Exception as e:
            logger.error(f"Gemini Betting Error: {e}")
            return self._rule_based_betting(player_state, table_state)

    async def decide_draw_action(
        self, player_state: PlayerState, table_state: TableState
    ) -> List[int]:
        if not self.client:
            return self._rule_based_draw(player_state)

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
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            if response.text:
                data = json.loads(response.text)
                return data.get("held_indices", [])
            else:
                return self._rule_based_draw(player_state)
        except Exception as e:
            logger.error(f"Gemini Draw Error: {e}")
            return self._rule_based_draw(player_state)

    async def decide_chat_response(
        self,
        message: str,
        history: List[str],
        player_state: PlayerState,
        table_state: TableState,
    ) -> str:
        if not self.client:
            return "Nice move."

        hand_str = self._format_hand(player_state.hand)
        history_str = "\n".join(history[-5:])

        prompt = f"""
        You are an AI player in a 5-Card Draw Poker game. 
        Your Name: {player_state.name}.
        Your Hand: {hand_str} ({player_state.hand.rank if player_state.hand else "Unknown"}).
        Game Phase: {table_state.phase}.
        Recent Chat History:
        {history_str}
        
        User just said: "{message}"
        
        Respond to the user or comment on the game in a short, trash-talking but professional poker player persona. 
        Keep it under 20 words.
        
        Respond ONLY with a JSON object:
        {{
            "response": "your message here"
        }}
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            if response.text:
                data = json.loads(response.text)
                return data.get("response", "Good luck, you'll need it.")
            else:
                return "Nice move."
        except Exception as e:
            logger.error(f"Gemini Chat Error: {e}")
            return "Nice move."
