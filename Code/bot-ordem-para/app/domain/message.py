from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Message:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = datetime.now()