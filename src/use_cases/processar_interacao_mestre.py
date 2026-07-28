from typing import Dict, Any, Optional
from src.domain.entities.memoria_sessao import MemoriaSessao
from src.domain.interfaces.llm_service import ILLMService
from src.domain.interfaces.rag_service import IRAGService
from src.domain.interfaces.audio_service import IAudioService

class ProcessarInteracaoMestreUseCase:
    """
    Caso de Uso Principal: Orquestra a interação entre o jogador e o Mestre IA.
    Recebe a ação do jogador, consulta memória/RAG, aciona o LLM e sintetiza a voz da resposta.
    """

    def __init__(
        self,
        llm_service: ILLMService,
        rag_service: Optional[IRAGService] = None,
        audio_service: Optional[IAudioService] = None,
        memoria: Optional[MemoriaSessao] = None
    ):
        self.llm_service = llm_service
        self.rag_service = rag_service
        self.audio_service = audio_service
        self.memoria = memoria or MemoriaSessao()

    async def executar(self, nome_jogador: str, fala_jogador: str) -> Dict[str, Any]:
        # 1. Registrar a fala no buffer da memória
        self.memoria.registrar_fala(nome_jogador, fala_jogador)

        # 2. Consultar regras no RAG se aplicável
        regras_contexto = ""
        if self.rag_service:
            regras_encontradas = self.rag_service.buscar_regras_ordem(fala_jogador)
            regras_contexto = "\n".join(regras_encontradas)

        # 3. Gerar resposta narrativa com o Gemini
        contexto_memoria = self.memoria.obter_contexto_compacto()
        resposta_llm = self.llm_service.gerar_resposta_mestre(
            prompt_sistema="",
            fala_jogador=f"{nome_jogador}: {fala_jogador}",
            contexto_memoria=contexto_memoria,
            regras_rag=regras_contexto
        )

        texto_narracao = resposta_llm.get("texto_narracao", "")

        # 4. Sintetizar áudio de resposta via Edge-TTS (se serviço disponível)
        audio_bytes = b""
        if self.audio_service and texto_narracao:
            audio_bytes = await self.audio_service.sintetizar_voz(texto_narracao)

        return {
            "texto_narracao": texto_narracao,
            "prompt_imagem": resposta_llm.get("prompt_imagem"),
            "audio_bytes": audio_bytes,
        }
