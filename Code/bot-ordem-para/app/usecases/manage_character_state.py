from app.domain.dtos import UpdateStatusDTO
from app.domain.session import Session
from app.ports.repository import ISessionRepository

class ManageCharacterStateUseCase:
    def __init__(self, session_repo: ISessionRepository):
        self.session_repo = session_repo

    async def update_status(self, dto: UpdateStatusDTO) -> Session:
        session = await self.session_repo.get_session(dto.session_id)
        if not session:
            raise ValueError(f"Sessão {dto.session_id} não encontrada")
        
        state = session.character_state
        if dto.type == "damage":
            state.take_damage(dto.amount)
        elif dto.type == "heal":
            max_hp = state.sheet.strength * 5
            state.current_hp = min(max_hp, state.current_hp + dto.amount)
        elif dto.type == "sanity_loss":
            state.lose_sanity(dto.amount)
        elif dto.type == "sanity_gain":
            max_sanity = state.sheet.presence * 10
            state.current_sanity = min(max_sanity, state.current_sanity + dto.amount)
            
        await self.session_repo.save_session(session)
        return session