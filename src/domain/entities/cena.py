from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Cena:
    """
    Representa a cena atual no RPG.
    """
    id: str
    titulo: str
    descricao_local: str
    investigacoes_chaves: List[str] = field(default_factory=list)
    em_combate: bool = False
    iniciativa_ordem: List[str] = field(default_factory=list)

    def adicionar_pista(self, pista: str):
        if pista not in self.investigacoes_chaves:
            self.investigacoes_chaves.append(pista)
