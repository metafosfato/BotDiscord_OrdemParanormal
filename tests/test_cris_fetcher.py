import pytest
from src.adapters.cris.cris_fetcher import CRISFetcherAdapter

def test_parsear_dict_cris():
    adapter = CRISFetcherAdapter()

    dados_mock_cris = {
        "id": "cris-12345",
        "nome": "Clarissa Leão",
        "jogador": "Mariana",
        "origem": "Acadêmica",
        "atributos": {
            "AGI": 2,
            "FOR": 1,
            "INT": 4,
            "PRE": 3,
            "VIG": 1
        },
        "vida_maxima": 24,
        "vida_atual": 24,
        "sanidade_maxima": 35,
        "sanidade_atual": 35,
        "pe_maximo": 12,
        "pe_atual": 12,
        "pericias": {
            "Ocultismo": 10,
            "Investigação": 10,
            "Percepção": 5
        }
    }

    personagem = adapter.parsear_dict(dados_mock_cris)

    assert personagem.id == "cris-12345"
    assert personagem.nome == "Clarissa Leão"
    assert personagem.atributos["INT"] == 4
    assert personagem.vida_maxima == 24
    assert personagem.sanidade_maxima == 35
    assert personagem.pericias["Ocultismo"] == 10

def test_importar_ficha_fallback_url_invalida():
    adapter = CRISFetcherAdapter()
    
    # URL fictícia para testar a resiliência do fallback
    personagem = adapter.importar_ficha_por_url("https://crisordemparanormal.com/ficha/invalid_test_url")

    assert personagem is not None
    assert "Agente" in personagem.nome
    assert personagem.vida_maxima > 0
