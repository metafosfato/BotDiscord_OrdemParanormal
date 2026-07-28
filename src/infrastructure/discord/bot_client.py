import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class OrdemBotClient(commands.Bot):
    """
    Cliente principal do Bot Discord para Ordem Paranormal RPG.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """
        Registra Cogs e sincroniza Slash Commands na inicialização.
        """
        from src.infrastructure.discord.cogs.session_cog import setup as setup_session_cog
        await setup_session_cog(self)

        # Sincroniza comandos Slash (app_commands)
        try:
            synced = await self.tree.sync()
            print(f"✅ Sincronizados {len(synced)} comando(s) Slash no Discord.")
        except Exception as e:
            print(f"⚠️ Erro ao sincronizar comandos Slash: {e}")

    async def on_ready(self):
        print(f"🟢 Bot online como: {self.user} (ID: {self.user.id})")
        print("🎮 Pronto para mestrar sessões de Ordem Paranormal.")
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="o Paranormal na escuridão..."
        )
        await self.change_presence(activity=activity)
