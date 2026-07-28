from typing import Optional
from src.domain.entities.resultado_dado import ResultadoDado
from src.domain.interfaces.personaje_repository import IPersonagemRepository

class ExecutarTesteMecanicoUseCase:
    """
    Caso de Uso: Executa deterministicamente a rolagem de um teste mecânico
    para um personagem na sessão de acordo com as regras de Ordem Paranormal.
    """

    def __init__(self, repository: IPersonagemRepository):
        self.repository = repository

    def executar(
        self,
        personagem_id: str,
        nome_pericia: str,
        atributo_override: Optional[str] = None,
        dt: Optional[int] = None
    ) -> ResultadoDado:
        personagem = self.repository.buscar_por_id(personagem_id)
        if not personagem:
            raise ValueError(f"Personagem com ID '{personagem_id}' não encontrado na sessão.")

        resultado = personagem.testar_pericia(
            nome_pericia=nome_pericia,
            atributo_override=atributo_override,
            dt=dt
        )
        
        # Persiste eventuais mudanças no personagem
        self.repository.salvar(personagem)
        return resultado
