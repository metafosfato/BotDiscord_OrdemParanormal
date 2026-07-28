from abc import ABC, abstractmethod

class IAudioService(ABC):
    """
    Interface para transcrever voz de jogadores (STT) e sintetizar a voz do Mestre (TTS).
    """

    @abstractmethod
    def transcrever_audio(self, pcm_bytes: bytes) -> str:
        """
        Converte áudio recebido do canal de voz em texto.
        """
        pass

    @abstractmethod
    async def sintetizar_voz(self, texto: str) -> bytes:
        """
        Converte a fala gerada pelo Mestre em fluxo de áudio (Edge-TTS).
        """
        pass
