import discord
from app.usecases.generate_narrative import GenerateNarrativeUseCase
from app.domain.dtos import PlayerActionDTO

class DiscordController(discord.Client):
    def __init__(self, narrative_use_case: GenerateNarrativeUseCase, intents: discord.Intents):
        super().__init__(intents=intents)
        self.narrative_use_case = narrative_use_case

    # Assinatura conforme diagrama: handlePlayerMessage(channelId: String, content: String)
    async def handle_player_message(self, channel_id: str, content: str) -> str:
        dto = PlayerActionDTO(session_id=channel_id, action_text=content)
        return await self.narrative_use_case.execute(dto)

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.content.startswith("!"):  # Ignore comandos de bot e o próprio bot
            return

        try:
            await message.channel.typing()
            response = await self.handle_player_message(message.channel.id, message.content)
            await message.channel.send(response)
        except Exception as e:
            print(f"❌ Erro no DiscordController: {e}")
            await message.channel.send("⚠️ Ocorreu um erro interno. Tente novamente.")