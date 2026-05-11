import aiohttp
from app.ports.llm import ILLMProvider
from app.config.settings import settings

class GrokAdapter(ILLMProvider):
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.85,
            "max_tokens": 1024
        }
        async with self.session.post(f"{self.base_url}/chat/completions", json=payload, headers={"Authorization": f"Bearer {self.api_key}"}) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"].strip()

    async def summarize_text(self, text: str) -> str:
        system = "Resuma esta sessão de RPG de Ordem Paranormal. Mantenha apenas fatos cruciais, localizações, personagens NPC e objetivos ativos. Seja extremamente conciso para otimizar tokens."
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ],
            "temperature": 0.3,
            "max_tokens": 512
        }
        async with self.session.post(f"{self.base_url}/chat/completions", json=payload, headers={"Authorization": f"Bearer {self.api_key}"}) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data["choices"][0]["message"]["content"].strip()