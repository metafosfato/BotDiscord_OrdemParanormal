from abc import ABC, abstractmethod

class IVisionService(ABC):
    """
    Interface para geração assíncrona de imagens das cenas do RPG.
    """

    @abstractmethod
    def gerar_imagem_cena(self, prompt_visual: str) -> str:
        """
        Gera uma ilustração da cena ou criatura e retorna o URL ou caminho da imagem.
        """
        pass
