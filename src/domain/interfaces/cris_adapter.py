from abc import ABC, abstractmethod
from src.domain.entities.personaje import Personagem

class ICRISAdapter(ABC):
    """
    Interface para importação e leitura de fichas públicas do C.R.I.S.
    """

    @abstractmethod
    def importar_ficha_por_url(self, url: str) -> Personagem:
        """
        Lê a página pública do CRIS e retorna uma instância da entidade Personagem.
        """
        pass
