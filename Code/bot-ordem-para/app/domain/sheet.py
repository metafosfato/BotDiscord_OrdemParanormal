from dataclasses import dataclass
from typing import Dict

@dataclass(frozen=True)
class Sheet:
    name: str
    strength: int
    agility: int
    presence: int
    skills: Dict[str, int]
    
    def to_dict(self) -> dict:
        return {"name": self.name, "strength": self.strength, "agility": self.agility, 
                "presence": self.presence, "skills": self.skills}