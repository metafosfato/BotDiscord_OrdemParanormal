from app.domain.session import Session
from app.domain.dtos import PlayerActionDTO
from app.ports.llm import ILLMProvider
from app.ports.repository import ISessionRepository
from app.usecases.summarize_history import SummarizeHistoryUseCase

class GenerateNarrativeUseCase:
    def __init__(self, llm_provider: ILLMProvider, session_repo: ISessionRepository, 
                 summarizer: SummarizeHistoryUseCase, history_limit: int = 10):
        self.llm_provider = llm_provider
        self.session_repo = session_repo
        self.summarizer = summarizer
        self.history_limit = history_limit

    async def execute(self, dto: PlayerActionDTO) -> str:
        session = await self.session_repo.get_session(dto.session_id)
        if not session:
            # Cria sessão padrão se não existir (fallback inicial)
            session = await self._create_default_session(dto.session_id)

        await self.summarizer.execute_if_needed(session)
        context = self._build_context(session)
        prompt = f"{context}\n\nJogador: {dto.action_text}\nNarrador:"
        
        response = await self.llm_provider.generate_response(prompt)
        session.add_interaction(dto.action_text, response)
        await self.session_repo.save_session(session)
        
        return response

    def _build_context(self, session: Session) -> str:
        status = session.character_state.format_for_prompt()
        summary = session.get_story_summary()
        recent = "\n".join([f"{m.role}: {m.content}" for m in session.get_recent_history(self.history_limit)])
        return f"📜 RESUMO DA CAMPANHA:\n{summary}\n\n STATUS DO PERSONAGEM:\n{status}\n\n💬 ÚLTIMAS INTERAÇÕES:\n{recent}"

    async def _create_default_session(self, session_id: str) -> Session:
        from app.domain.sheet import Sheet
        from app.domain.character_state import CharacterState
        sheet = Sheet(name="Personagem Genérico", strength=3, agility=3, presence=3, skills={})
        state = CharacterState(sheet=sheet, current_hp=30, current_sanity=30)
        session = Session(id=session_id, character_state=state)
        await self.session_repo.save_session(session)
        return session