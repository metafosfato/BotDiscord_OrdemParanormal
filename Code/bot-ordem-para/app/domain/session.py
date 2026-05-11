from dataclasses import dataclass, field
from typing import List
from app.domain.character_state import CharacterState
from app.domain.message import Message

@dataclass
class Session:
    id: str
    character_state: CharacterState
    history: List[Message] = field(default_factory=list)
    story_summary: str = ""

    def add_interaction(self, player_action: str, ai_response: str) -> None:
        self.history.append(Message(role="user", content=player_action))
        self.history.append(Message(role="assistant", content=ai_response))

    def get_recent_history(self, limit: int) -> List[Message]:
        return self.history[-limit:]

    def get_story_summary(self) -> str:
        return self.story_summary

    def update_summary(self, new_summary: str, truncate_history_at: int) -> None:
        self.story_summary = new_summary
        self.history = self.history[-truncate_history_at]

    def is_history_oversized(self, threshold: int) -> bool:
        return len(self.history) > threshold