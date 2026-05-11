from app.domain.session import Session
from app.ports.llm import ILLMProvider
from app.ports.repository import ISessionRepository

class SummarizeHistoryUseCase:
    def __init__(self, llm_provider: ILLMProvider, session_repo: ISessionRepository, threshold: int = 50):
        self.llm_provider = llm_provider
        self.session_repo = session_repo
        self.threshold = threshold

    async def execute_if_needed(self, session: Session) -> None:
        if session.is_history_oversized(self.threshold):
            history_text = "\n".join([f"{m.role}: {m.content}" for m in session.history])
            new_summary = await self.llm_provider.summarize_text(history_text)
            session.update_summary(new_summary, truncate_history_at=self.threshold // 2)
            await self.session_repo.save_session(session)