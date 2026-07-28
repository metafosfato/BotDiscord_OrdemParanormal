from abc import ABC, abstractmethod
from typing import List

class IRAGService(ABC):
    """
    Interface para consulta vetorial às regras de Ordem Paranormal no Supabase.
    """

    @abstractmethod
    def buscar_regras_ordem(self, consulta: str, top_k: int = 3) -> List[str]:
        """
        Retorna os trechos de regras mais relevantes para a dúvida/mecânica solicitada.
        """
        pass
