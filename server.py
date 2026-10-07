import os
import glob
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from rag_pipeline import (
    extract_pdf_data,
    chunk_document,
    tokenize_and_embed,
    store_in_supabase_and_local,
    retrieve_candidates,
    generate_augmented_response,
    LOCAL_VECTOR_STORE,
    EMBEDDING_DIM,
    EMBEDDING_MODEL_NAME,
    SUPABASE_URL,
    OPENROUTER_API_KEY
)

app = FastAPI(
    title="RAG Laiane API",
    description="Backend didático para o pipeline RAG de notas fiscais com FastEmbed, PGVector e OpenRouter",
    version="1.0.0"
)

# Configuração de CORS para permitir acesso do Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class IngestRequest(BaseModel):
    document_name: Optional[str] = None  # Se None, ingere todos os 4 PDFs

@app.get("/api/status")
def get_system_status():
    """Retorna o status dos componentes sem expor nenhuma credencial sensível."""
    return {
        "status": "online",
        "system_name": "RAG Laiane",
        "embedding_model": {
            "name": EMBEDDING_MODEL_NAME,
            "dimensions": EMBEDDING_DIM,
            "provider": "FastEmbed"
        },
        "llm_provider": {
            "name": "OpenRouter",
            "model": "openrouter/router",
            "is_configured": bool(OPENROUTER_API_KEY)
        },
        "database": {
            "name": "Supabase PostgreSQL + PGVector",
            "is_configured": bool(SUPABASE_URL),
            "stored_chunks_count": len(LOCAL_VECTOR_STORE)
        }
    }

@app.get("/api/documents")
def list_available_documents():
    """Lista todos os PDFs de notas fiscais disponíveis no ambiente."""
    pdf_paths = glob.glob("data/invoices/*.pdf")
    docs = []
    for p in pdf_paths:
        name = os.path.basename(p)
        size_kb = round(os.path.getsize(p) / 1024, 2)
        # Verifica se já há chunks indexados para este documento
        chunks_count = sum(1 for c in LOCAL_VECTOR_STORE if c["document_name"] == name)
        docs.append({
            "filename": name,
            "size_kb": size_kb,
            "is_indexed": chunks_count > 0,
            "chunks_count": chunks_count
        })
    return {"documents": docs, "total": len(docs)}

@app.post("/api/ingest")
def process_ingestion(request: IngestRequest):
    """
    Executa o pipeline completo de ingestão e retorna dados detalhados para cada etapa:
    INGESTÃO -> CHUNKING -> TOKENIZAÇÃO -> EMBEDDING -> ÍNDICE VETORIAL
    """
    pdf_paths = glob.glob("data/invoices/*.pdf")
    if request.document_name:
        pdf_paths = [p for p in pdf_paths if os.path.basename(p) == request.document_name]

    if not pdf_paths:
        raise HTTPException(status_code=404, detail="Nenhum documento PDF encontrado para ingestão.")

    pipeline_results = []

    for path in pdf_paths:
        doc_filename = os.path.basename(path)
        
        # 1. INGESTÃO / OCR & EXTRAÇÃO
        extracted = extract_pdf_data(path)
        
        # 2. CHUNKING
        chunks = chunk_document(extracted)
        
        # 3. & 4. TOKENIZAÇÃO & EMBEDDINGS (FastEmbed)
        enriched_chunks = tokenize_and_embed(chunks)
        
        # 5. ÍNDICE VETORIAL (Supabase + Local)
        storage_result = store_in_supabase_and_local(enriched_chunks)

        pipeline_results.append({
            "document_name": doc_filename,
            "steps": {
                "step_1_ingestion": {
                    "step_name": "Ingestão e Extração de Dados (OCR/Parser)",
                    "status": "completed",
                    "raw_text_preview": extracted["raw_text"][:300] + "...",
                    "structured_data": extracted["structured_data"]
                },
                "step_2_chunking": {
                    "step_name": "Divisão Semântica em Chunks",
                    "status": "completed",
                    "total_chunks": len(chunks),
                    "chunks": [
                        {
                            "chunk_index": c["chunk_index"],
                            "chunk_type": c["chunk_type"],
                            "content": c["content"]
                        } for c in chunks
                    ]
                },
                "step_3_tokenization": {
                    "step_name": "Tokenização",
                    "status": "completed",
                    "total_tokens_estimated": sum(c.get("token_count", 0) for c in enriched_chunks),
                    "chunks_tokens": [
                        {
                            "chunk_index": c["chunk_index"],
                            "token_count": c["token_count"]
                        } for c in enriched_chunks
                    ]
                },
                "step_4_embedding": {
                    "step_name": "Geração de Embeddings (FastEmbed)",
                    "status": "completed",
                    "model": EMBEDDING_MODEL_NAME,
                    "dimensions": EMBEDDING_DIM,
                    "samples": [
                        {
                            "chunk_index": c["chunk_index"],
                            "embedding_sample": c["embedding_sample"],
                            "dimensions": c["embedding_dim"]
                        } for c in enriched_chunks
                    ]
                },
                "step_5_vector_index": {
                    "step_name": "Armazenamento no Índice Vetorial",
                    "status": "completed",
                    "supabase": storage_result["supabase_message"],
                    "total_active_chunks": storage_result["total_stored_chunks"]
                }
            }
        })

    return {
        "success": True,
        "processed_documents_count": len(pipeline_results),
        "total_active_chunks": len(LOCAL_VECTOR_STORE),
        "results": pipeline_results
    }

@app.post("/api/query")
def process_rag_query(req: QueryRequest):
    """
    Executa a consulta pedagógica completa:
    PERGUNTA -> TOKENIZAÇÃO -> EMBEDDING -> RETRIEVAL -> PROMPT AUMENTADO -> LLM -> RESPOSTA
    """
    query_text = req.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    # 1 & 2. PERGUNTA -> TOKENIZAÇÃO / EMBEDDING DA QUERY & RETRIEVAL (TOP_K = 5)
    candidates, query_emb = retrieve_candidates(query_text, top_k=req.top_k or 5)

    # 3 & 4. PROMPT AUMENTADO -> LLM (OpenRouter) -> RESPOSTA
    llm_result = generate_augmented_response(query_text, candidates)

    return {
        "query": query_text,
        "steps": {
            "step_1_query_embedding": {
                "step_name": "Tokenização e Embedding da Pergunta",
                "embedding_dimensions": len(query_emb),
                "embedding_sample": [round(x, 4) for x in query_emb[:8]] if query_emb else []
            },
            "step_2_retrieval": {
                "step_name": "Busca Vetorial por Similaridade (Top-K = 5)",
                "top_k": req.top_k or 5,
                "retrieved_count": len(candidates),
                "candidates": [
                    {
                        "document_name": c["document_name"],
                        "chunk_index": c["chunk_index"],
                        "chunk_type": c["chunk_type"],
                        "similarity_score": c["similarity"],
                        "content": c["content"],
                        "metadata": c.get("metadata", {})
                    } for c in candidates
                ]
            },
            "step_3_prompt_augmented": {
                "step_name": "Construção do Prompt Aumentado",
                "prompt_text": llm_result["prompt_augmented"]
            },
            "step_4_llm_response": {
                "step_name": "Geração da Resposta pelo LLM",
                "status": llm_result["status"],
                "relevant_candidates_count": llm_result["relevant_candidates_count"],
                "answer": llm_result["answer"]
            }
        },
        "final_answer": llm_result["answer"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
