import os
from typing import Optional
from supabase import create_client, Client

def get_supabase_client() -> Optional[Client]:
    """
    Retorna a instância do cliente Supabase pré-configurada com as chaves do .env.
    Se as chaves não estiverem configuradas, retorna None de forma segura.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        print(f"⚠️ Aviso: Não foi possível conectar ao Supabase: {e}")
        return None
