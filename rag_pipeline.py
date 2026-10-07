import os
import re
import json
import numpy as np
import pandas as pd
import pdfplumber
import httpx
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from fastembed import TextEmbedding

load_dotenv()

# Carregar variáveis com segurança
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = (os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")).strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()

# Inicialização global do modelo FastEmbed (384 dimensões, multilíngue)
EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
print(f"[RAG] Inicializando modelo FastEmbed: {EMBEDDING_MODEL_NAME}...")
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
EMBEDDING_DIM = 384

# Armazenamento em memória local sincronizado (garante fallback imediato e rápido)
LOCAL_VECTOR_STORE: List[Dict[str, Any]] = []

def extract_pdf_data(pdf_path: str) -> Dict[str, Any]:
    """
    Etapa 1: INGESTÃO / OCR & EXTRAÇÃO
    Extrai o texto bruto e estrutura os campos das notas fiscais.
    """
    filename = os.path.basename(pdf_path)
    full_text = ""
    tables_found = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += f"\n--- Página {page_idx + 1} ---\n" + text
            tables = page.extract_tables()
            for t in tables:
                if t:
                    tables_found.append(t)

    # Extração de campos via regex e tabelas
    number_match = re.search(r"Número da Nota:\s*([A-Za-z0-9\-]+)", full_text)
    date_match = re.search(r"Emissão:\s*(\d{2}/\d{2}/\d{4})", full_text)
    total_match = re.search(r"VALOR TOTAL DA NOTA:\s*(R\$\s*[\d\.\,]+)", full_text)
    
    provider_name = "N/A"
    cnpj_value = "N/A"
    items_tabular = []

    # Extração precisa das tabelas detectadas pelo pdfplumber
    for t in tables_found:
        if not t or len(t) == 0:
            continue
        # Tabela 1: Emitente / Destinatário
        first_cell = str(t[0][0])
        if "EMITENTE / FORNECEDOR:" in first_cell:
            lines = [l.strip() for l in first_cell.split("\n") if l.strip()]
            if len(lines) >= 2:
                provider_name = lines[1]
            cnpj_m = re.search(r"CNPJ:\s*([\d\.\/\-]+)", first_cell)
            if cnpj_m:
                cnpj_value = cnpj_m.group(1)

        # Tabela de Itens (possui cabeçalho com 'Item' ou 'Descrição')
        if any("Descrição" in str(col) or "Descricao" in str(col) or "Item" in str(col) for col in t[0]):
            headers = [str(c).strip() if c else f"col_{i}" for i, c in enumerate(t[0])]
            for row in t[1:]:
                clean_row = [str(cell).strip() if cell else "" for cell in row]
                if len(clean_row) == len(headers):
                    items_tabular.append(dict(zip(headers, clean_row)))

    # Fallback de CNPJ via texto
    if cnpj_value == "N/A":
        cnpj_m = re.search(r"CNPJ:\s*([\d\.\/\-]+)", full_text)
        if cnpj_m:
            cnpj_value = cnpj_m.group(1)

    df_items = pd.DataFrame(items_tabular)

    return {
        "document_name": filename,
        "raw_text": full_text.strip(),
        "structured_data": {
            "invoice_number": number_match.group(1) if number_match else "N/A",
            "issue_date": date_match.group(1) if date_match else "N/A",
            "provider": provider_name,
            "cnpj": cnpj_value,
            "total_value": total_match.group(1) if total_match else "N/A",
            "items_table": items_tabular
        }
    }

def chunk_document(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Etapa 2: CHUNKING DIDÁTICO
    Divide a nota fiscal em blocos de contexto semanticamente coesos.
    """
    doc_name = extracted_data["document_name"]
    s = extracted_data["structured_data"]
    chunks = []

    # Chunk 1: Metadados da Nota Fiscal e Fornecedor
    c1_content = (
        f"Nota Fiscal: {s['invoice_number']}\n"
        f"Documento: {doc_name}\n"
        f"Data de Emissão: {s['issue_date']}\n"
        f"Fornecedor / Emitente: {s['provider']}\n"
        f"CNPJ do Fornecedor: {s['cnpj']}"
    )
    chunks.append({
        "document_name": doc_name,
        "chunk_index": 0,
        "chunk_type": "Cabecalho_Fornecedor",
        "content": c1_content,
        "metadata": {
            "invoice_number": s["invoice_number"],
            "provider": s["provider"],
            "type": "header"
        }
    })

    # Chunk 2: Itens, Produtos e Serviços
    items_desc = []
    for it in s["items_table"]:
        desc = it.get("Descrição") or it.get("Descricao") or ""
        qtd = it.get("Qtd") or ""
        unit = it.get("Valor Unit.") or ""
        tot = it.get("Total") or ""
        items_desc.append(f"- Produto/Serviço: {desc} | Quantidade: {qtd} | Valor Unitário: {unit} | Subtotal: {tot}")
    
    items_text = "\n".join(items_desc) if items_desc else "Nenhum item discriminado."
    c2_content = (
        f"Nota Fiscal: {s['invoice_number']} - Produtos e Serviços:\n"
        f"Fornecedor: {s['provider']}\n"
        f"{items_text}"
    )
    chunks.append({
        "document_name": doc_name,
        "chunk_index": 1,
        "chunk_type": "Itens_Produtos",
        "content": c2_content,
        "metadata": {
            "invoice_number": s["invoice_number"],
            "items_count": len(s["items_table"]),
            "type": "items"
        }
    })

    # Chunk 3: Valores Totais e Observações
    # Localizar observações no raw_text
    notes_match = re.search(r"INFORMAÇÕES COMPLEMENTARES.*?\n(.*)", extracted_data["raw_text"], re.DOTALL)
    notes_text = notes_match.group(1).strip() if notes_match else "Sem observações adicionais."

    c3_content = (
        f"Nota Fiscal: {s['invoice_number']} - Totais e Informações Adicionais:\n"
        f"Fornecedor: {s['provider']}\n"
        f"Valor Total da Nota: {s['total_value']}\n"
        f"Observações e Condições: {notes_text}"
    )
    chunks.append({
        "document_name": doc_name,
        "chunk_index": 2,
        "chunk_type": "Totais_Observacoes",
        "content": c3_content,
        "metadata": {
            "invoice_number": s["invoice_number"],
            "total_value": s["total_value"],
            "type": "totals"
        }
    })

    return chunks

def tokenize_and_embed(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Etapa 3 & 4: TOKENIZAÇÃO & EMBEDDINGS (FastEmbed)
    Gera as representações vetoriais de cada chunk.
    """
    texts = [c["content"] for c in chunks]
    embeddings = list(embedding_model.embed(texts))

    enriched_chunks = []
    for c, emb in zip(chunks, embeddings):
        emb_list = [float(x) for x in emb]
        # Estimativa de tokens para visualização didática
        token_count = len(c["content"].split()) + int(len(c["content"]) * 0.2)
        c_copy = dict(c)
        c_copy["token_count"] = token_count
        c_copy["embedding"] = emb_list
        c_copy["embedding_sample"] = [round(x, 4) for x in emb_list[:8]] # Primeiras 8 dimensões para didática
        c_copy["embedding_dim"] = len(emb_list)
        enriched_chunks.append(c_copy)

    return enriched_chunks

def store_in_supabase_and_local(chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Etapa 5: ÍNDICE VETORIAL (Supabase PGVector + Local Vector Store)
    Persiste os vetores no Supabase e atualiza o armazenamento local.
    """
    global LOCAL_VECTOR_STORE
    
    # Atualiza local vector store in-place
    for c in chunks:
        # Remove versão anterior se já existir
        LOCAL_VECTOR_STORE[:] = [x for x in LOCAL_VECTOR_STORE if not (x["document_name"] == c["document_name"] and x["chunk_index"] == c["chunk_index"])]
        LOCAL_VECTOR_STORE.append(c)

    supabase_status = "not_attempted"
    supabase_message = ""

    # Tentativa de inserção no Supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            records = []
            for c in chunks:
                records.append({
                    "document_name": c["document_name"],
                    "chunk_index": c["chunk_index"],
                    "chunk_type": c["chunk_type"],
                    "content": c["content"],
                    "metadata": c["metadata"],
                    "embedding": c["embedding"]
                })
            
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            # Insere na tabela invoice_chunks
            resp = httpx.post(
                f"{SUPABASE_URL}/rest/v1/invoice_chunks",
                headers=headers,
                json=records,
                timeout=10.0
            )
            if resp.status_code in (200, 201):
                supabase_status = "synced"
                supabase_message = f"Sucesso: {len(records)} chunks inseridos no Supabase PGVector."
            else:
                supabase_status = "table_pending"
                supabase_message = f"Tabela remota no Supabase requer criação do schema.sql (Status: {resp.status_code}). Vetores indexados localmente com sucesso."
        except Exception as e:
            supabase_status = "error"
            supabase_message = f"Conexão com Supabase: {str(e)}. Armazenamento local ativo."
    else:
        supabase_status = "missing_env"
        supabase_message = "Credenciais do Supabase não configuradas."

    return {
        "supabase_status": supabase_status,
        "supabase_message": supabase_message,
        "total_stored_chunks": len(LOCAL_VECTOR_STORE)
    }

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calcula a similaridade de cosseno entre dois vetores."""
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def retrieve_candidates(query: str, top_k: int = 5) -> Tuple[List[Dict[str, Any]], List[float]]:
    """
    Etapa de Retrieval:
    PERGUNTA -> EMBEDDING DA PERGUNTA -> BUSCA VETORIAL -> TOP_K = 5
    """
    if not LOCAL_VECTOR_STORE:
        return [], []

    # 1. Gera embedding da pergunta
    query_emb = list(embedding_model.embed([query]))[0]
    query_emb_list = [float(x) for x in query_emb]

    # 2. Busca por similaridade
    scored_chunks = []
    for c in LOCAL_VECTOR_STORE:
        sim = cosine_similarity(query_emb_list, c["embedding"])
        item = dict(c)
        item["similarity"] = round(sim, 4)
        scored_chunks.append(item)

    # 3. Ordena decrescente pelo score de similaridade
    scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
    top_candidates = scored_chunks[:top_k]

    return top_candidates, query_emb_list

def generate_augmented_response(query: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Etapa: PROMPT AUMENTADO -> OPENROUTER LLM -> RESPOSTA
    Aplica estritamente a regra: Se não houver contexto suficiente,
    responde exatamente 'Sem dados disponíveis na base'.
    """
    # Limiar mínimo de similaridade para considerar o candidato relevante
    SIMILARITY_THRESHOLD = 0.28
    relevant_candidates = [c for c in candidates if c["similarity"] >= SIMILARITY_THRESHOLD]

    if not relevant_candidates:
        return {
            "answer": "Sem dados disponíveis na base",
            "prompt_augmented": "N/A - Consulta sem dados suficientes recuperados.",
            "status": "no_context",
            "relevant_candidates_count": 0
        }

    # Monta o contexto a partir dos chunks recuperados
    context_sections = []
    for idx, c in enumerate(relevant_candidates):
        context_sections.append(
            f"--- [CHUNK {idx+1} | Documento: {c['document_name']} | Similaridade: {c['similarity']}] ---\n{c['content']}"
        )
    context_text = "\n\n".join(context_sections)

    # Prompt aumentado estrito
    prompt_augmented = f"""Você é um assistente RAG especializado em infraestrutura e notas fiscais de carregadores para veículos elétricos (Wallbox AC, estações ultrarrápidas DC, cabos e instalações elétricas).
Sua instrução mandatória é responder à pergunta do usuário baseando-se EXCLUSIVAMENTE nas informações fornecidas no CONTEXTO RECUPERADO abaixo.

REGRAS:
1. Responda apenas com base no CONTEXTO.
2. Não utilize conhecimento prévio externo ao contexto.
3. Se o contexto não contiver dados suficientes para responder com certeza à pergunta, responda EXATAMENTE: "Sem dados disponíveis na base".
4. Seja claro, objetivo e cite a nota fiscal ou fornecedor quando relevante.

CONTEXTO RECUPERADO:
{context_text}

PERGUNTA DO USUÁRIO:
{query}

RESPOSTA:"""

    # Chamada ao OpenRouter
    if not OPENROUTER_API_KEY:
        return {
            "answer": "Erro: OPENROUTER_API_KEY não configurada no backend.",
            "prompt_augmented": prompt_augmented,
            "status": "error",
            "relevant_candidates_count": len(relevant_candidates)
        }

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "RAG Laiane",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "user", "content": prompt_augmented}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        if response.status_code == 200:
            result = response.json()
            answer_text = result["choices"][0]["message"]["content"].strip()
            return {
                "answer": answer_text,
                "prompt_augmented": prompt_augmented,
                "status": "success",
                "relevant_candidates_count": len(relevant_candidates)
            }
        else:
            return {
                "answer": f"Erro na chamada OpenRouter: Status {response.status_code}",
                "prompt_augmented": prompt_augmented,
                "status": "llm_error",
                "relevant_candidates_count": len(relevant_candidates)
            }
    except Exception as e:
        return {
            "answer": f"Falha na comunicação com o LLM: {str(e)}",
            "prompt_augmented": prompt_augmented,
            "status": "exception",
            "relevant_candidates_count": len(relevant_candidates)
        }
