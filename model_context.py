import json
from typing import List, Dict

class ConversationMemory:
    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    def update(self, user_input: str, bot_response: str):
        self.history.append({"user": user_input, "bot": bot_response})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def get_context(self) -> str:
        return "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in self.history])

    def save(self, file_path: str = "conversation.json"):
        with open(file_path, "w") as f:
            json.dump(self.history, f)

    def load(self, file_path: str = "conversation.json"):
        try:
            with open(file_path, "r") as f:
                self.history = json.load(f)[:self.max_history]
        except FileNotFoundError:
            self.history = []