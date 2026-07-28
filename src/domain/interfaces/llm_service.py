from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class ILLMService(ABC):
    """
    Interface para comunicação com o LLM (Gemini).
    """

    @abstractmethod
    def gerar_resposta_mestre(
        self,
        prompt_sistema: str,
        fala_jogador: str,
        contexto_memoria: str,
        regras_rag: str,
        ferramentas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Gera a narração do Mestre ou solicita chamada de função (Function Calling).
        Retorna dicionário contendo 'texto_narracao', 'prompt_imagem' e/ou 'chamada_funcao'.
        """
        pass

    @abstractmethod
    def sintetizar_memoria(self, historico_falas: List[str]) -> str:
        """
        Sintetiza falas da sessão em fatos de memória de longo prazo.
        """
        pass
