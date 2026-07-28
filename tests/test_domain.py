import pytest
from src.domain.entities.personaje import Personagem
from src.domain.entities.memoria_sessao import MemoriaSessao

def test_rolagem_teste_pericia_atributo_positivo():
    # Arrange: Personagem com INT = 3 e Ocultismo = +5
    agente = Personagem(
        id="123",
        nome="Arthur Cervero",
        atributos={"INT": 3, "AGI": 1, "FOR": 1, "PRE": 1, "VIG": 1},
        pericias={"Ocultismo": 5}
    )

    # Injetamos dados fixos [12, 18, 4] no dice_fn
    mock_dice = lambda n: [12, 18, 4]

    # Act
    resultado = agente.testar_pericia("Ocultismo", dt=20, dice_fn=mock_dice)

    # Assert
    assert resultado.valor_atributo == 3
    assert resultado.dados_rolados == [12, 18, 4]
    assert resultado.dado_escolhido == 18  # Maior dado selecionado
    assert resultado.bonificacao == 5
    assert resultado.valor_total == 23  # 18 + 5
    assert resultado.sucesso is True  # 23 >= 20

def test_rolagem_teste_pericia_atributo_zero_desvantagem():
    # Arrange: Personagem com FOR = 0 e Luta = 0 (Atributo 0 = rola 2d20 e pega o menor)
    agente = Personagem(
        id="456",
        nome="Kaiser",
        atributos={"INT": 3, "AGI": 2, "FOR": 0, "PRE": 1, "VIG": 1},
        pericias={"Luta": 0}
    )

    # Mock de dados [15, 6] -> deve escolher 6 (menor dado)
    mock_dice = lambda n: [15, 6]

    # Act
    resultado = agente.testar_pericia("Luta", dt=10, dice_fn=mock_dice)

    # Assert
    assert resultado.valor_atributo == 0
    assert len(resultado.dados_rolados) == 2
    assert resultado.dado_escolhido == 6  # Menor dado selecionado devido a desvantagem
    assert resultado.valor_total == 6
    assert resultado.sucesso is False  # 6 < 10

def test_receber_dano_e_cura():
    agente = Personagem(id="789", nome="Joo", vida_maxima=30, vida_atual=30)
    
    # Sofre 20 de dano -> Vida cai para 10 (<= 15 -> machucado)
    agente.receber_dano(20)
    assert agente.vida_atual == 10
    assert "machucado" in agente.condicoes

    # Curado em 15 HP -> Vida vai para 25 (> 15 -> remove machucado)
    agente.curar_vida(15)
    assert agente.vida_atual == 25
    assert "machucado" not in agente.condicoes

def test_perder_sanidade():
    agente = Personagem(id="101", nome="Dante", sanidade_maxima=40, sanidade_atual=40)
    
    agente.perder_sanidade(25)
    assert agente.sanidade_atual == 15
    assert "perturbado" in agente.condicoes

def test_gastar_pe():
    agente = Personagem(id="202", nome="Rubens", pe_maximo=10, pe_atual=10)
    
    assert agente.gastar_pe(4) is True
    assert agente.pe_atual == 6
    assert agente.gastar_pe(8) is False  # Não tem PE suficiente
    assert agente.pe_atual == 6

def test_memoria_sessao_buffer():
    memoria = MemoriaSessao(max_ultimas_falas=3)
    memoria.registrar_fala("Arthur", "Vejo um símbolo na parede.")
    memoria.registrar_fala("Dante", "Vou investigar a energia paranormal.")
    memoria.registrar_fala("Kaiser", "Preparo minha arma.")
    memoria.registrar_fala("Mestre", "O símbolo começa a brilhar em vermelho sangue.")

    # Deve manter apenas as últimas 3 falas
    assert len(memoria.ultimas_falas) == 3
    assert "Arthur" not in memoria.ultimas_falas[0]
    assert "Dante" in memoria.ultimas_falas[0]
