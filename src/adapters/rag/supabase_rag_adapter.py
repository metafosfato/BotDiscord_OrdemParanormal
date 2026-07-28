import os
from typing import List, Optional
from google import genai
from supabase import Client
from src.domain.interfaces.rag_service import IRAGService
from src.infrastructure.database.supabase_client import get_supabase_client

# Trechos de fallback de regras de Ordem Paranormal quando o banco não estiver conectado
REGRAS_FALLBACK = [
    "REGRAS DE SANIDADE: Sempre que um agente presencia um horror paranormal ou sofre dano mental, ele realiza um teste de Vontade contra a DT da Presença Perturbadora. Em caso de fracasso, reduz Sanidade equivalente ao dano da criatura.",
    "REGRAS DE OCULTISMO E RITUAIS: Lançar um ritual consome Pontos de Esforço (PE). Se o agente não possuir PE suficiente, o ritual falha automaticamente. Rituais exigem um componente ritualístico do elemento correspondente (Sangue, Morte, Conhecimento, Energia).",
    "REGRAS DE COMBATE E ROLAGENS: Testes de ataque ou perícia rolam N d20s onde N é o valor do Atributo correspondente. Seleciona-se o maior dado e soma-se o bônus da perícia. Atributo 0 rola 2 d20s com desvantagem (selecionando o menor)."
]

class SupabaseRAGAdapter(IRAGService):
    """
    Adaptador de busca vetorial (RAG) utilizando Supabase pgvector e Gemini Embeddings.
    """

    def __init__(
        self,
        supabase_client: Optional[Client] = None,
        api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-004"
    ):
        self.supabase = supabase_client or get_supabase_client()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.embedding_model = embedding_model

        if self.api_key:
            self.genai_client = genai.Client(api_key=self.api_key)
        else:
            self.genai_client = None

    def gerar_embedding(self, texto: str) -> Optional[List[float]]:
        """
        Gera o vetor de embedding (768 dimensões) utilizando o Gemini text-embedding-004.
        """
        if not self.genai_client or not texto:
            return None

        try:
            response = self.genai_client.models.embed_content(
                model=self.embedding_model,
                contents=texto
            )
            if response and response.embedding:
                return response.embedding.values
        except Exception as e:
            print(f"⚠️ Erro ao gerar embedding no Gemini: {e}")

        return None

    def buscar_regras_ordem(self, consulta: str, top_k: int = 3) -> List[str]:
        """
        Busca os trechos de regras mais relevantes no Supabase via vetorização cosenoidal.
        """
        embedding = self.gerar_embedding(consulta)

        if self.supabase and embedding:
            try:
                rpc_response = self.supabase.rpc(
                    "match_regras_ordem",
                    {
                        "query_embedding": embedding,
                        "match_threshold": 0.2,
                        "match_count": top_k
                    }
                ).execute()

                data = rpc_response.data
                if data and isinstance(data, list):
                    resultados = [item["conteudo"] for item in data if "conteudo" in item]
                    if resultados:
                        return resultados
            except Exception as e:
                print(f"⚠️ Erro na consulta RPC no Supabase: {e}")

        # Retorno de fallback caso Supabase esteja offline ou sem dados
        return self._filtrar_fallback_local(consulta, top_k)

    def _filtrar_fallback_local(self, consulta: str, top_k: int) -> List[str]:
        """
        Filtra os trechos de fallback com base em palavras-chave da consulta.
        """
        consulta_lower = consulta.lower()
        relevantes = []

        for regra in REGRAS_FALLBACK:
            if any(term in consulta_lower for term in ["sanidade", "loucura", "mental", "vontade"]) and "SANIDADE" in regra:
                relevantes.append(regra)
            elif any(term in consulta_lower for term in ["ritual", "ocultismo", "pe", "esforço"]) and "OCULTISMO" in regra:
                relevantes.append(regra)
            elif any(term in consulta_lower for term in ["dado", "rolagem", "ataque", "luta"]) and "COMBATE" in regra:
                relevantes.append(regra)

        return relevantes if relevantes else REGRAS_FALLBACK[:top_k]
