-- ========================================================
-- SCHEMA DE BUSCA VETORIAL (RAG) - ORDEM PARANORMAL RPG
-- Execute este script no SQL Editor do seu console Supabase
-- ========================================================

-- 1. Habilitar a extensão pgvector para suporte a vetores
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Criar a tabela de regras do sistema de Ordem Paranormal
CREATE TABLE IF NOT EXISTS regras_ordem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conteudo TEXT NOT NULL,
    categoria VARCHAR(100) DEFAULT 'Geral',
    fonte VARCHAR(200) DEFAULT 'Livro de Regras',
    embedding VECTOR(768), -- Dimensão padrão do Gemini text-embedding-004
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Criar índice de busca vetorial IVFFlat / HNSW para alta performance
CREATE INDEX IF NOT EXISTS idx_regras_ordem_embedding 
ON regras_ordem 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- 4. Função RPC para busca vetorial por similaridade cosenoidal
CREATE OR REPLACE FUNCTION match_regras_ordem (
    query_embedding VECTOR(768),
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    conteudo TEXT,
    categoria VARCHAR,
    fonte VARCHAR,
    similarity FLOAT
)
LANGUAGE sql STABLE
AS $$
    SELECT
        regras_ordem.id,
        regras_ordem.conteudo,
        regras_ordem.categoria,
        regras_ordem.fonte,
        1 - (regras_ordem.embedding <=> query_embedding) AS similarity
    FROM regras_ordem
    WHERE 1 - (regras_ordem.embedding <=> query_embedding) > match_threshold
    ORDER BY regras_ordem.embedding <=> query_embedding
    LIMIT match_count;
$$;
