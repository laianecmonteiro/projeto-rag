import json
import glob
from rag_pipeline import (
    extract_pdf_data,
    chunk_document,
    tokenize_and_embed,
    store_in_supabase_and_local,
    retrieve_candidates,
    generate_augmented_response,
    LOCAL_VECTOR_STORE
)

def run_tests():
    print("=== TESTE DO PIPELINE RAG: EMPRESA DE CARREGADORES DE CARROS ELÉTRICOS ===")
    
    # 1. Ingestão dos 4 PDFs
    pdfs = glob.glob("data/invoices/*.pdf")
    print(f"[TESTE] Encontrados {len(pdfs)} arquivos de notas fiscais de carregadores elétricos.")
    assert len(pdfs) == 4, f"Esperado 4 PDFs, encontrados {len(pdfs)}"

    for pdf in pdfs:
        print(f"\n-> Processando: {pdf}")
        extracted = extract_pdf_data(pdf)
        print(f"   [Etapa 1: Ingestão/Extração] Nota: {extracted['structured_data']['invoice_number']} | Fornecedor: {extracted['structured_data']['provider']} | Total: {extracted['structured_data']['total_value']}")
        
        chunks = chunk_document(extracted)
        print(f"   [Etapa 2: Chunking] {len(chunks)} chunks gerados.")
        
        enriched = tokenize_and_embed(chunks)
        print(f"   [Etapa 3 & 4: Tokenização & FastEmbed] {len(enriched)} embeddings gerados com dimensão {enriched[0]['embedding_dim']}.")
        
        storage = store_in_supabase_and_local(enriched)
        print(f"   [Etapa 5: Vetor/Banco] Status: {storage['supabase_status']} | Total na base: {storage['total_stored_chunks']}")

    print(f"\n[SUCESSO] Total de chunks no índice vetorial: {len(LOCAL_VECTOR_STORE)}")

    # 2. Teste de Pergunta Relevante 1 (Estação DC 60kW FastEletro)
    print("\n-----------------------------------------------------")
    q1 = "Qual é o valor total e o fornecedor da estação de carga rápida DC 60kW?"
    print(f"[TESTE CONSULTA 1] Pergunta: '{q1}'")
    candidates_1, _ = retrieve_candidates(q1, top_k=5)
    print(f"-> Top-{len(candidates_1)} candidatos recuperados:")
    for idx, c in enumerate(candidates_1):
        print(f"   {idx+1}. [{c['document_name']}] Score: {c['similarity']} | {c['chunk_type']}")
    
    resp_1 = generate_augmented_response(q1, candidates_1)
    print(f"-> Resposta LLM:\n{resp_1['answer']}")

    # 3. Teste de Pergunta Relevante 2 (Wallbox 7.4kW VoltCharge)
    print("\n-----------------------------------------------------")
    q2 = "Quantos carregadores Wallbox residenciais 7.4kW foram faturados e qual a potência dos carregadores comerciais?"
    print(f"[TESTE CONSULTA 2] Pergunta: '{q2}'")
    candidates_2, _ = retrieve_candidates(q2, top_k=5)
    print(f"-> Top-{len(candidates_2)} candidatos recuperados:")
    for idx, c in enumerate(candidates_2):
        print(f"   {idx+1}. [{c['document_name']}] Score: {c['similarity']} | {c['chunk_type']}")
    
    resp_2 = generate_augmented_response(q2, candidates_2)
    print(f"-> Resposta LLM:\n{resp_2['answer']}")

    # 4. Teste de Pergunta Fora do Domínio (Regra 'Sem dados disponíveis na base')
    print("\n-----------------------------------------------------")
    q3 = "Qual a velocidade máxima de um foguete espacial para a Lua?"
    print(f"[TESTE CONSULTA 3 (SEM DADOS)] Pergunta: '{q3}'")
    candidates_3, _ = retrieve_candidates(q3, top_k=5)
    print(f"-> Top-{len(candidates_3)} candidatos recuperados:")
    for idx, c in enumerate(candidates_3):
        print(f"   {idx+1}. [{c['document_name']}] Score: {c['similarity']} | {c['chunk_type']}")
    
    resp_3 = generate_augmented_response(q3, candidates_3)
    print(f"-> Resposta LLM (Deve ser 'Sem dados disponíveis na base'):\n{resp_3['answer']}")

    print("\n=====================================================")
    print("TESTE DO PIPELINE RAG CONCLUÍDO COM SUCESSO!")
    print("=====================================================")

if __name__ == "__main__":
    run_tests()
