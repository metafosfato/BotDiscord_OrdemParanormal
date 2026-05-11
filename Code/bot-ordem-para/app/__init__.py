import asyncio
import aiohttp
import motor.motor_asyncio
import discord
from app.config.settings import settings
from app.adapters.llm.grok_adapter import GrokAdapter
from app.adapters.db.mongo_repository import MongoSessionRepository
from app.usecases.summarize_history import SummarizeHistoryUseCase
from app.usecases.generate_narrative import GenerateNarrativeUseCase
from app.controllers.discord_controller import DiscordController

async def main():
    async with aiohttp.ClientSession() as http_session, motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI) as mongo_client:
        db = mongo_client[settings.DB_NAME]

        # Ports/Adapters
        llm_adapter = GrokAdapter(http_session)
        session_repo = MongoSessionRepository(db)

        # Use Cases
        summarizer = SummarizeHistoryUseCase(llm_adapter, session_repo, threshold=settings.SUMMARY_THRESHOLD)
        narrative_uc = GenerateNarrativeUseCase(llm_adapter, session_repo, summarizer, history_limit=settings.SESSION_HISTORY_LIMIT)

        # Controller
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        bot = DiscordController(narrative_use_case=narrative_uc, intents=intents)
        await bot.start(settings.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())