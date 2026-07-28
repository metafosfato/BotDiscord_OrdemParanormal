import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from src.domain.entities.resultado_dado import ResultadoDado

PERICIA_ATRIBUTO_PADRAO: Dict[str, str] = {
    # Agilidade
    "Acrobacia": "AGI",
    "Crime": "AGI",
    "Furtividade": "AGI",
    "Pilotagem": "AGI",
    "Pontaria": "AGI",
    "Reflexos": "AGI",
    # Força
    "Atletismo": "FOR",
    "Luta": "FOR",
    # Intelecto
    "Atualidades": "INT",
    "Ciências": "INT",
    "Investigação": "INT",
    "Medicina": "INT",
    "Ocultismo": "INT",
    "Sobrevivência": "INT",
    "Tática": "INT",
    "Tecnologia": "INT",
    # Presença
    "Adestramento": "PRE",
    "Artes": "PRE",
    "Diplomacia": "PRE",
    "Enganação": "PRE",
    "Intimidação": "PRE",
    "Intuição": "PRE",
    "Percepção": "PRE",
    "Religião": "PRE",
    "Vontade": "PRE",
    # Vigor
    "Fortitude": "VIG",
}

@dataclass
class Personagem:
    """
    Entidade pura representando um personagem de Ordem Paranormal.
    Todas as ações de dano, sanidade e rolagens de dados utilizam
    cálculos determinísticos em código Python.
    """
    id: str
    nome: str
    jogador: str = ""
    origem: str = ""
    trilha: str = ""

    # Atributos (AGI, FOR, INT, PRE, VIG)
    atributos: Dict[str, int] = field(default_factory=lambda: {
        "AGI": 1,
        "FOR": 1,
        "INT": 1,
        "PRE": 1,
        "VIG": 1,
    })

    # Status de Combate & Recursos
    vida_maxima: int = 20
    vida_atual: int = 20
    sanidade_maxima: int = 20
    sanidade_atual: int = 20
    pe_maximo: int = 5
    pe_atual: int = 5
    defesa: int = 10

    # Bônus de Perícias (ex: {"Ocultismo": 5, "Percepção": 10})
    pericias: Dict[str, int] = field(default_factory=dict)
    
    # Condições ativas (ex: ["machucado", "perturbado"])
    condicoes: List[str] = field(default_factory=list)

    def obter_valor_atributo(self, nome_atributo: str) -> int:
        attr_upper = nome_atributo.upper()
        return self.atributos.get(attr_upper, 0)

    def obter_bonus_pericia(self, nome_pericia: str) -> int:
        for k, v in self.pericias.items():
            if k.lower() == nome_pericia.lower():
                return v
        return 0

    def testar_pericia(
        self,
        nome_pericia: str,
        atributo_override: Optional[str] = None,
        dt: Optional[int] = None,
        margem_ameaca: int = 20,
        dice_fn: Optional[Callable[[int], List[int]]] = None
    ) -> ResultadoDado:
        """
        Executa deterministicamente um teste de perícia segundo as regras de Ordem Paranormal.
        - Se Atributo > 0: Rola N d20s e escolhe o MAIOR.
        - Se Atributo == 0: Rola 2 d20s e escolhe o MENOR (Desvantagem).
        - Soma o bônus de perícia.
        """
        # Identifica atributo associado
        attr_name = atributo_override or PERICIA_ATRIBUTO_PADRAO.get(nome_pericia, "INT")
        attr_value = self.obter_valor_atributo(attr_name)
        bonus = self.obter_bonus_pericia(nome_pericia)

        # Quantidade de dados a rolar
        qtd_dados = attr_value if attr_value > 0 else 2

        # Geração dos dados
        if dice_fn:
            dados = dice_fn(qtd_dados)
        else:
            dados = [random.randint(1, 20) for _ in range(qtd_dados)]

        # Seleção do dado
        if attr_value > 0:
            dado_escolhido = max(dados)
        else:
            dado_escolhido = min(dados)

        total = dado_escolhido + bonus
        foi_critico = dado_escolhido >= margem_ameaca
        foi_desastre = (dados == [1, 1]) if attr_value == 0 else (dado_escolhido == 1 and len(dados) == 1)

        return ResultadoDado(
            nome_pericia=nome_pericia,
            nome_atributo=attr_name,
            valor_atributo=attr_value,
            dados_rolados=dados,
            dado_escolhido=dado_escolhido,
            bonificacao=bonus,
            valor_total=total,
            dt=dt,
            foi_critico=foi_critico,
            foi_desastre=foi_desastre,
            margem_ameaca=margem_ameaca,
        )

    def receber_dano(self, quantidade: int) -> int:
        dano_real = max(0, quantidade)
        self.vida_atual = max(0, self.vida_atual - dano_real)
        if self.vida_atual <= self.vida_maxima / 2 and "machucado" not in self.condicoes:
            self.condicoes.append("machucado")
        return self.vida_atual

    def curar_vida(self, quantidade: int) -> int:
        cura = max(0, quantidade)
        self.vida_atual = min(self.vida_maxima, self.vida_atual + cura)
        if self.vida_atual > self.vida_maxima / 2 and "machucado" in self.condicoes:
            self.condicoes.remove("machucado")
        return self.vida_atual

    def perder_sanidade(self, quantidade: int) -> int:
        perda = max(0, quantidade)
        self.sanidade_atual = max(0, self.sanidade_atual - perda)
        if self.sanidade_atual <= self.sanidade_maxima / 2 and "perturbado" not in self.condicoes:
            self.condicoes.append("perturbado")
        return self.sanidade_atual

    def gastar_pe(self, quantidade: int) -> bool:
        if self.pe_atual >= quantidade:
            self.pe_atual -= quantidade
            return True
        return False
