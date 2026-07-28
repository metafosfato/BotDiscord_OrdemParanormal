from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ResultadoDado:
    """
    Representa o resultado de uma rolagem de dados em Ordem Paranormal.
    Toda a lógica de seleção de maior/menor d20 e cálculo é determinística.
    """
    nome_pericia: str
    nome_atributo: str
    valor_atributo: int
    dados_rolados: List[int]
    dado_escolhido: int
    bonificacao: int
    valor_total: int
    dt: Optional[int] = None
    sucesso: Optional[bool] = None
    foi_critico: bool = False
    foi_desastre: bool = False
    margem_ameaca: int = 20

    def __post_init__(self):
        if self.dt is not None and self.sucesso is None:
            self.sucesso = self.valor_total >= self.dt
