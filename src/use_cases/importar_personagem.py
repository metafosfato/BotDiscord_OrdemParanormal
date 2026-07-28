from src.domain.entities.personaje import Personagem
from src.domain.interfaces.cris_adapter import ICRISAdapter
from src.domain.interfaces.personaje_repository import IPersonagemRepository

class ImportarPersonagemCRISUseCase:
    """
    Caso de Uso: Importa a ficha pública do CRIS via URL e armazena no repositório da sessão.
    """

    def __init__(self, cris_adapter: ICRISAdapter, repository: IPersonagemRepository):
        self.cris_adapter = cris_adapter
        self.repository = repository

    def executar(self, url: str) -> Personagem:
        personagem = self.cris_adapter.importar_ficha_por_url(url)
        self.repository.salvar(personagem)
        return personagem
