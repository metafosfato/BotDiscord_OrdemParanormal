import os
import sys
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Adiciona a raiz do projeto ao path do python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.adapters.rag.supabase_rag_adapter import SupabaseRAGAdapter
from src.infrastructure.database.supabase_client import get_supabase_client

# Regras base padrão de Ordem Paranormal para população inicial
REGRAS_INICIAIS = [
    {
        "categoria": "Sanidade & Presença Perturbadora",
        "fonte": "Livro de Regras Capitulo 3",
        "conteudo": "Presença Perturbadora: Ao encontrar uma criatura paranormal pela primeira vez na cena, o agente deve fazer um teste de Vontade contra a DT da criatura. Se falhar, perde Sanidade inteira da Presença Perturbadora. Se passar, reduz a perda pela metade. Agentes que chegam a 0 de Sanidade entram em estado de Enlouquecendo."
    },
    {
        "categoria": "Rituais & Ocultismo",
        "fonte": "Livro de Regras Capitulo 4",
        "conteudo": "Conjurando Rituais: Para conjurar um ritual, o agente gasta o custo em Pontos de Esforço (PE) correspondente (Círculo 1: 1 PE, Círculo 2: 3 PE, Círculo 3: 6 PE, Círculo 4: 10 PE). O agente precisa estar segurando um componente ritualístico do elemento do ritual (Sangue, Morte, Conhecimento ou Energia)."
    },
    {
        "categoria": "Mecânica de Rolagens",
        "fonte": "Livro de Regras Capitulo 1",
        "conteudo": "Testes de Perícia: Rola-se uma quantidade de dados d20 igual ao valor do Atributo testado. Escolhe-se o maior dado e soma-se o bônus da Perícia. Se o Atributo for 0, rolam-se 2 d20s e escolhe-se o menor dado (Desvantagem). Se o dado base escolhido for 20 natural (ou atingir a Margem de Ameaça), o teste é um Crítico."
    },
    {
        "categoria": "Combate & Defesa",
        "fonte": "Livro de Regras Capitulo 5",
        "conteudo": "Ações de Combate: Em seu turno, um agente pode realizar uma Ação Padrão, uma Ação de Movimento e Ações Livres. A Defesa de um personagem é calculada como 10 + Agilidade + Proteção. Reações de defesa incluem Esquivar (adiciona Reflexos na Defesa) ou Bloquear (reduz dano com Fortitude)."
    },
    {
        "categoria": "Elementos do Paranormal",
        "fonte": "Livro de Regras Capitulo 2",
        "conteudo": "O Outro Lado é composto por 4 Elementos: Sangue (Sentimento, Paixão, Dor - forte contra Conhecimento), Morte (Tempo, Entropia - forte contra Sangue), Conhecimento (Razão, Consciência - forte contra Energia) e Energia (Caos, Transformação - forte contra Morte)."
    }
]

def ingerir_regras():
    load_dotenv()
    supabase = get_supabase_client()
    if not supabase:
        print("❌ Erro: Supabase não está configurado no arquivo .env (SUPABASE_URL e SUPABASE_KEY são necessários).")
        return

    rag_adapter = SupabaseRAGAdapter(supabase_client=supabase)
    if not rag_adapter.genai_client:
        print("❌ Erro: GEMINI_API_KEY necessária no .env para gerar embeddings.")
        return

    print("🚀 Iniciando ingestão das regras de Ordem Paranormal no Supabase...")
    inseridos = 0

    for item in REGRAS_INICIAIS:
        conteudo = item["conteudo"]
        categoria = item["categoria"]
        fonte = item["fonte"]

        embedding = rag_adapter.gerar_embedding(conteudo)
        if not embedding:
            print(f"⚠️ Falha ao gerar embedding para: {categoria}")
            continue

        data = {
            "conteudo": conteudo,
            "categoria": categoria,
            "fonte": fonte,
            "embedding": embedding
        }

        try:
            res = supabase.table("regras_ordem").insert(data).execute()
            print(f"✅ Ingerido [{categoria}]: {conteudo[:60]}...")
            inseridos += 1
        except Exception as e:
            print(f"❌ Erro ao gravar no Supabase [{categoria}]: {e}")

    print(f"\n🎉 Ingestão concluída com sucesso! {inseridos} bloco(s) de regras salvos na tabela 'regras_ordem'.")

if __name__ == "__main__":
    ingerir_regras()
