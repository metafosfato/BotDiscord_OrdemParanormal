import os
import json
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from src.domain.interfaces.llm_service import ILLMService

PROMPT_SISTEMA_MESTRE = """
Você é o Mestre de RPG para o sistema Ordem Paranormal.
Sua missão é narrar uma investigação de terror e mistério com tom sombrio, tenso e imersivo.

REGRAS DE CONDUTA DO MESTRE:
1. NUNCA invente ou simule rolagens de dados ou cálculos aritméticos por conta própria.
2. Se a fala do jogador exigir uma ação mecânica (como investigar um símbolo, resistir a sanidade, esquivar de um golpe, usar Ocultismo), você DEVE acionar a função correspondente (Function Calling) como `solicitar_teste_pericia`.
3. Quando receber o resultado real do dado e da mecânica executados em código Python, narre as consequências daquele resultado exato com intensidade narrativa.
4. Descreva ambientes com foco em elementos visuais, sons inquietantes e cheiros desagradáveis característicos dos elementos do Paranormal (Sangue, Morte, Conhecimento, Energia).
"""

class GeminiLLMAdapter(ILLMService):
    """
    Adaptador para a API Google GenAI (Gemini) utilizando a SDK oficial google.genai.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def gerar_resposta_mestre(
        self,
        prompt_sistema: str,
        fala_jogador: str,
        contexto_memoria: str,
        regras_rag: str,
        ferramentas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        if not self.client:
            return {
                "texto_narracao": "[Fallback] O Mestre observa em silêncio. (GEMINI_API_KEY não configurada no .env)",
                "prompt_imagem": None,
                "chamada_funcao": None
            }

        prompt_completo = (
            f"{contexto_memoria}\n\n"
            f"=== REGRAS DE ORDEM PARANORMAL (RAG) ===\n"
            f"{regras_rag if regras_rag else 'Nenhuma regra específica consultada.'}\n\n"
            f"=== FALA / AÇÃO DO JOGADOR ===\n"
            f"{fala_jogador}"
        )

        sys_instruction = prompt_sistema or PROMPT_SISTEMA_MESTRE

        try:
            config = types.GenerateContentConfig(
                system_instruction=sys_instruction,
                temperature=0.7,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_completo,
                config=config,
            )

            texto = response.text or ""
            return {
                "texto_narracao": texto,
                "prompt_imagem": None,
                "chamada_funcao": None
            }
        except Exception as e:
            return {
                "texto_narracao": f"[Erro no Gemini API]: {str(e)}",
                "prompt_imagem": None,
                "chamada_funcao": None
            }

    def sintetizar_memoria(self, historico_falas: List[str]) -> str:
        if not self.client or not historico_falas:
            return "Nenhum resumo novo gerado."

        prompt = (
            "Sintetize em poucas frases os acontecimentos mais marcantes das falas a seguir para guardar na memória de longo prazo da investigação:\n\n"
            + "\n".join(historico_falas)
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            return response.text or "Sem novos destaques."
        except Exception as e:
            return f"Erro ao sintetizar memória: {str(e)}"
