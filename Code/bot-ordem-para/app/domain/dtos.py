from dataclasses import dataclass

@dataclass
class PlayerActionDTO:
    session_id: str
    action_text: str

@dataclass
class UpdateStatusDTO:
    session_id: str
    amount: int
    type: str  # "damage", "sanity", "heal", "insanity"