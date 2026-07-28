from typing import Dict, List, Optional
from src.domain.entities.personaje import Personagem
from src.domain.interfaces.personaje_repository import IPersonagemRepository

class MemoriaPersonagemRepository(IPersonagemRepository):
    """
    Repositório em memória para guardar o estado dinâmico dos personagens da sessão.
    """

    def __init__(self):
        self._personagens: Dict[str, Personagem] = {}

    def salvar(self, personagem: Personagem) -> None:
        self._personagens[personagem.id] = personagem

    def buscar_por_id(self, id: str) -> Optional[Personagem]:
        return self._personagens.get(id)

    def listar_todos(self) -> List[Personagem]:
        return list(self._personagens.values())
