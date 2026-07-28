import os
import sys
import io
import asyncio
from dotenv import load_dotenv
from src.infrastructure.discord.bot_client import OrdemBotClient

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

load_dotenv()

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERRO: DISCORD_TOKEN não encontrado no arquivo .env!")
        sys.exit(1)

    print("🚀 Iniciando Bot Ordem Paranormal...")
    bot = OrdemBotClient()

    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("\n👋 Bot encerrado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao rodar o bot: {e}")

if __name__ == "__main__":
    main()
