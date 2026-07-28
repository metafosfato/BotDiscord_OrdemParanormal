from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.personaje import Personagem

class IPersonagemRepository(ABC):
    """
    Interface de repositório para persistência/recuperação do estado dos personagens na sessão.
    """

    @abstractmethod
    def salvar(self, personagem: Personagem) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, id: str) -> Optional[Personagem]:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Personagem]:
        pass
