import edge_tts
from src.domain.interfaces.audio_service import IAudioService

class EdgeTTSAdapter(IAudioService):
    """
    Adaptador de Sintetizador de Voz utilizando Edge-TTS.
    Gera voz em português com tom solene/sombrio sem custo de API.
    """

    def __init__(self, voice: str = "pt-BR-AntonioNeural"):
        self.voice = voice

    def transcrever_audio(self, pcm_bytes: bytes) -> str:
        """
        STT Transcrição (Placeholder para pipeline STT de voz).
        """
        return "Transcrição de áudio não implementada."

    async def sintetizar_voz(self, texto: str) -> bytes:
        """
        Sintetiza texto em fluxo de áudio MP3/PCM usando a voz configurada.
        """
        if not texto or not texto.strip():
            return b""

        communicate = edge_tts.Communicate(texto, self.voice)
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        
        return bytes(audio_data)
