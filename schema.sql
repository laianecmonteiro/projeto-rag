-- =========================================================================
-- ESQUEMA DO BANCO DE DADOS SUPABASE / POSTGRESQL + PGVECTOR
-- Projeto: RAG Laiane
-- Dimensão do Embedding: 384 (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
-- =========================================================================

-- 1. Habilitar a extensão PGVector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Tabela de armazenamento de chunks de notas fiscais
CREATE TABLE IF NOT EXISTS public.invoice_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_name TEXT NOT NULL,
    chunk_index INT NOT NULL,
    chunk_type TEXT DEFAULT 'section',
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(384),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Índice vetorial HNSW para otimização da busca por similaridade (distância de cosseno)
CREATE INDEX IF NOT EXISTS invoice_chunks_embedding_idx 
ON public.invoice_chunks 
USING hnsw (embedding vector_cosine_ops);

-- 4. Função RPC para Retrieval Vetorial (Top-K = 5 com scores de similaridade de cosseno)
CREATE OR REPLACE FUNCTION public.match_invoice_chunks (
    query_embedding vector(384),
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_name TEXT,
    chunk_index INT,
    chunk_type TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.document_name,
        c.chunk_index,
        c.chunk_type,
        c.content,
        c.metadata,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM public.invoice_chunks c
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
