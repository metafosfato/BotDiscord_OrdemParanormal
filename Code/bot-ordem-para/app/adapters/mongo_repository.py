import motor.motor_asyncio
from app.ports.repository import ISessionRepository
from app.domain.session import Session, Message
from app.domain.character_state import CharacterState
from app.domain.sheet import Sheet
from app.config.settings import settings

class MongoSessionRepository(ISessionRepository):
    def __init__(self, db: motor.motor_asyncio.AsyncIOMotorDatabase):
        self.sessions_col = db.sessions
        self.sheets_col = db.sheets

    async def get_session(self, session_id: str) -> Session | None:
        doc = await self.sessions_col.find_one({"id": session_id})
        if not doc:
            return None

        # Busca a ficha estática referenciada (FK)
        sheet_doc = await self.sheets_col.find_one({"_id": doc["sheetId"]})
        if not sheet_doc:
            raise ValueError(f"Ficha sheetId {doc['sheetId']} não encontrada")

        sheet = Sheet(
            name=sheet_doc["name"],
            strength=sheet_doc["strength"],
            agility=sheet_doc["agility"],
            presence=sheet_doc["presence"],
            skills=sheet_doc["skills"]
        )
        char_state = CharacterState(
            sheet=sheet,
            current_hp=doc["currentHp"], # Ajustado
            current_sanity=doc["currentSanity"], # Ajustado
            inventory=doc.get("inventory", [])
        )
        history = [Message(role=m["role"], content=m["content"], timestamp=m["timestamp"]) for m in doc.get("history", [])]
        
        return Session(
            id=doc["id"],
            character_state=char_state,
            history=history,
            story_summary=doc.get("storySummary", "")
        )

    async def save_session(self, session: Session) -> None:
        history = [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in session.history]
        doc = {
            "id": session.id,
            "sheetId": session.character_state.sheet.name,  # Simplificação: usando name como ref. Em produção, usar _id real
            "currentHp": session.character_state.current_hp,
            "currentSanity": session.character_state.current_sanity,
            "inventory": session.character_state.inventory,
            "history": history,
            "storySummary": session.story_summary
        }
        await self.sessions_col.update_one({"id": session.id}, {"$set": doc}, upsert=True)