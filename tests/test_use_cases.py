import pytest
import asyncio
from src.adapters.cris.cris_fetcher import CRISFetcherAdapter
from src.adapters.repository.memory_repository import MemoriaPersonagemRepository
from src.adapters.llm.gemini_adapter import GeminiLLMAdapter
from src.adapters.audio.edge_tts_adapter import EdgeTTSAdapter
from src.use_cases.importar_personagem import ImportarPersonagemCRISUseCase
from src.use_cases.executar_teste_mecanico import ExecutarTesteMecanicoUseCase
from src.use_cases.processar_interacao_mestre import ProcessarInteracaoMestreUseCase

def test_use_case_importar_e_testar_personagem():
    repo = MemoriaPersonagemRepository()
    cris_adapter = CRISFetcherAdapter()
    
    # 1. Importar personagem
    importar_uc = ImportarPersonagemCRISUseCase(cris_adapter, repo)
    personagem = importar_uc.executar("https://crisordemparanormal.com/ficha/mock_test")
    
    assert personagem is not None
    assert repo.buscar_por_id(personagem.id) is not None

    # 2. Executar teste de perícia determinístico
    teste_uc = ExecutarTesteMecanicoUseCase(repo)
    resultado = teste_uc.executar(personagem.id, "Ocultismo", dt=15)

    assert resultado is not None
    assert resultado.nome_pericia == "Ocultismo"
    assert resultado.valor_total >= 1

def test_use_case_processar_interacao_mestre():
    llm = GeminiLLMAdapter()
    audio = EdgeTTSAdapter()
    use_case = ProcessarInteracaoMestreUseCase(llm_service=llm, audio_service=audio)

    res = asyncio.run(use_case.executar("Arthur", "Tento acender minha lanterna no corredor escuro."))

    assert "texto_narracao" in res
    assert isinstance(res["audio_bytes"], bytes)
