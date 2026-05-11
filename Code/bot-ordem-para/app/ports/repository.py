from abc import ABC, abstractmethod
from typing import Optional
from app.domain.session import Session

class ISessionRepository(ABC):
    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Session]: ...
    
    @abstractmethod
    def save_session(self, session: Session) -> None: ...