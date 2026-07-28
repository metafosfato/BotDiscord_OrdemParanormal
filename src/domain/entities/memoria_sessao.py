from dataclasses import dataclass, field
from typing import List

@dataclass
class MemoriaSessao:
    """
    Gerencia a memória de curto e longo prazo da sessão de RPG.
    Previne estouro de contexto e alucinação da LLM.
    """
    fatos_relevantes: List[str] = field(default_factory=list)
    ultimas_falas: List[str] = field(default_factory=list)
    resumo_acumulado: str = ""
    max_ultimas_falas: int = 10

    def registrar_fala(self, autor: str, conteudo: str):
        self.ultimas_falas.append(f"{autor}: {conteudo}")
        if len(self.ultimas_falas) > self.max_ultimas_falas:
            self.ultimas_falas.pop(0)

    def adicionar_insight(self, fato: str):
        if fato not in self.fatos_relevantes:
            self.fatos_relevantes.append(fato)

    def obter_contexto_compacto(self) -> str:
        """
        Retorna a síntese da sessão para ser injetada no prompt do Mestre.
        """
        fatos_str = "\n".join([f"- {f}" for f in self.fatos_relevantes])
        return (
            f"=== SÍNTESE DA SESSÃO ===\n"
            f"{self.resumo_acumulado}\n\n"
            f"=== FATOS MARCANTES ===\n"
            f"{fatos_str if fatos_str else 'Nenhum fato marcante registrado ainda.'}"
        )
