import pytest
from src.adapters.rag.supabase_rag_adapter import SupabaseRAGAdapter

def test_rag_adapter_fallback_local():
    # Testa se o adaptador RAG retorna respostas úteis de regras mesmo sem Supabase configurado
    adapter = SupabaseRAGAdapter(supabase_client=None, api_key=None)

    # Consulta sobre sanidade
    regras_sanidade = adapter.buscar_regras_ordem("Como funciona o teste de sanidade e vontade?")
    assert len(regras_sanidade) > 0
    assert any("SANIDADE" in r for r in regras_sanidade)

    # Consulta sobre rituais
    regras_rituais = adapter.buscar_regras_ordem("Qual o custo de PE para lançar um ritual de Sangue?")
    assert len(regras_rituais) > 0
    assert any("OCULTISMO" in r or "RITUAIS" in r for r in regras_rituais)

    # Consulta genérica
    regras_genericas = adapter.buscar_regras_ordem("Como funciona o combate?")
    assert len(regras_genericas) > 0
