from dataclasses import dataclass, field
from typing import List
from app.domain.sheet import Sheet

@dataclass
class CharacterState:
    sheet: Sheet
    current_hp: int
    current_sanity: int
    inventory: List[str] = field(default_factory=list)

    def take_damage(self, amount: int) -> None:
        self.current_hp = max(0, self.current_hp - amount)

    def lose_sanity(self, amount: int) -> None:
        self.current_sanity = max(0, self.current_sanity - amount)

    def format_for_prompt(self) -> str:
        return (
            f"Personagem: {self.sheet.name}\n"
            f"HP: {self.current_hp} | Sanidade: {self.current_sanity}\n"
            f"Inv: {', '.join(self.inventory) if self.inventory else 'Nenhum'}"
        )