'use client';

import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export default function Home() {
  const [activeTab, setActiveTab] = useState('ingest'); // 'ingest', 'query', 'architecture'
  
  // Estados do Sistema
  const [systemStatus, setSystemStatus] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingStatus, setLoadingStatus] = useState(true);

  // Estados de Ingestão
  const [selectedDoc, setSelectedDoc] = useState('ALL');
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestionResults, setIngestionResults] = useState(null);
  const [ingestActiveStep, setIngestActiveStep] = useState(0);

  // Estados de Consulta / Chat
  const [queryInput, setQueryInput] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      role: 'assistant',
      content: 'Olá! Sou o assistente RAG especializado nas notas fiscais e equipamentos de recarga para carros elétricos (Wallbox Residencial 7.4kW, estações rápidas DC 60kW, cabos Tipo 2 e instalações para condomínios). Como posso ajudar hoje?',
      time: 'Agora'
    }
  ]);
  const [lastQueryData, setLastQueryData] = useState(null);
  const [queryActiveStep, setQueryActiveStep] = useState(0);

  // Carregar dados iniciais do backend
  useEffect(() => {
    fetchSystemInfo();
  }, []);

  const fetchSystemInfo = async () => {
    try {
      setLoadingStatus(true);
      const [resStatus, resDocs] = await Promise.all([
        fetch(`${API_BASE_URL}/api/status`).then(r => r.json()).catch(() => null),
        fetch(`${API_BASE_URL}/api/documents`).then(r => r.json()).catch(() => null)
      ]);
      if (resStatus) setSystemStatus(resStatus);
      if (resDocs && resDocs.documents) setDocuments(resDocs.documents);
    } catch (e) {
      console.error("Erro ao carregar dados do backend:", e);
    } finally {
      setLoadingStatus(false);
    }
  };

  // Disparar Ingestão Didática
  const handleRunIngestion = async () => {
    setIsIngesting(true);
    setIngestionResults(null);
    setIngestActiveStep(1);

    try {
      // Simulação visual de progresso da esteira
      const timer1 = setTimeout(() => setIngestActiveStep(2), 600);
      const timer2 = setTimeout(() => setIngestActiveStep(3), 1200);
      const timer3 = setTimeout(() => setIngestActiveStep(4), 1800);

      const payload = selectedDoc === 'ALL' ? {} : { document_name: selectedDoc };
      const res = await fetch(`${API_BASE_URL}/api/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      setIngestActiveStep(5);
      setIngestionResults(data);
      fetchSystemInfo();
    } catch (err) {
      alert("Erro ao executar ingestão: " + err.message);
    } finally {
      setIsIngesting(false);
    }
  };

  // Enviar Pergunta na Consulta RAG
  const handleSendQuery = async (customQuery = null) => {
    const q = customQuery || queryInput;
    if (!q.trim()) return;

    const userMsg = {
      role: 'user',
      content: q,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setChatMessages(prev => [...prev, userMsg]);
    if (!customQuery) setQueryInput('');
    setIsQuerying(true);
    setQueryActiveStep(1);

    try {
      // Visualização das etapas de consulta
      const t1 = setTimeout(() => setQueryActiveStep(2), 300);
      const t2 = setTimeout(() => setQueryActiveStep(3), 600);
      const t3 = setTimeout(() => setQueryActiveStep(4), 900);

      const res = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 5 })
      });
      const data = await res.json();

      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);

      setQueryActiveStep(5);
      setLastQueryData(data);

      const assistantMsg = {
        role: 'assistant',
        content: data.final_answer,
        isNoContext: data.final_answer === "Sem dados disponíveis na base",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setChatMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setChatMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Erro ao comunicar com o backend: ' + err.message,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsQuerying(false);
    }
  };

  return (
    <main className="app-container">
      {/* HEADER PRINCIPAL */}
      <header className="app-header">
        <div className="logo-section">
          <div className="logo-badge">⚡</div>
          <div>
            <h1 className="logo-title">RAG Laiane</h1>
            <p className="logo-subtitle">Infraestrutura & Carregadores de Veículos Elétricos</p>
          </div>
        </div>

        <div className="system-status-bar">
          <div className="status-pill">
            <span className="pulse-dot"></span>
            <span>{systemStatus?.database.stored_chunks_count || 0} Chunks Indexados</span>
          </div>
          <div className="status-pill" style={{ borderColor: 'rgba(56, 189, 248, 0.3)', color: '#38BDF8', background: 'rgba(56, 189, 248, 0.1)' }}>
            <span>FastEmbed (384D)</span>
          </div>
          <div className="status-pill" style={{ borderColor: 'rgba(168, 85, 247, 0.3)', color: '#A855F7', background: 'rgba(168, 85, 247, 0.1)' }}>
            <span>OpenRouter LLM</span>
          </div>
        </div>
      </header>

      {/* NAVEGAÇÃO DE ABAS */}
      <nav className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'ingest' ? 'active' : ''}`}
          onClick={() => setActiveTab('ingest')}
          id="tab-ingest"
        >
          <span>📥</span> 1. Ingestão de Documentos
        </button>
        <button
          className={`tab-btn ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
          id="tab-query"
        >
          <span>💬</span> 2. Consulta & Chat RAG
        </button>
        <button
          className={`tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
          onClick={() => setActiveTab('architecture')}
          id="tab-architecture"
        >
          <span>🧠</span> 3. Conceitos & Arquitetura
        </button>
      </nav>

      {/* ========================================================= */}
      {/* ABA 1: INGESTÃO DE DOCUMENTOS */}
      {/* ========================================================= */}
      {activeTab === 'ingest' && (
        <section>
          {/* STEPPER DINÂMICO DE INGESTÃO */}
          <div className="pipeline-stepper">
            <div className={`step-node ${ingestActiveStep >= 1 ? 'completed' : ''} ${ingestActiveStep === 1 ? 'active' : ''}`}>
              <div className="step-number">1</div>
              <div className="step-label">
                <span className="step-name">INGESTÃO</span>
                <span className="step-sub">PDF / OCR & Parser</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${ingestActiveStep >= 2 ? 'completed' : ''} ${ingestActiveStep === 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-label">
                <span className="step-name">CHUNKING</span>
                <span className="step-sub">Segmentação Semântica</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${ingestActiveStep >= 3 ? 'completed' : ''} ${ingestActiveStep === 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-label">
                <span className="step-name">TOKENIZAÇÃO</span>
                <span className="step-sub">Subpalavras / Tokens</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${ingestActiveStep >= 4 ? 'completed' : ''} ${ingestActiveStep === 4 ? 'active' : ''}`}>
              <div className="step-number">4</div>
              <div className="step-label">
                <span className="step-name">EMBEDDING</span>
                <span className="step-sub">FastEmbed (384D)</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${ingestActiveStep >= 5 ? 'completed' : ''} ${ingestActiveStep === 5 ? 'active' : ''}`}>
              <div className="step-number">5</div>
              <div className="step-label">
                <span className="step-name">ÍNDICE VETORIAL</span>
                <span className="step-sub">Supabase PGVector</span>
              </div>
            </div>
          </div>

          <div className="grid-2col">
            {/* PAINEL DE CONTROLE DE INGESTÃO */}
            <div className="card-panel">
              <div className="panel-header">
                <h2 className="panel-title">📄 Seleção de Documentos para Ingestão</h2>
                <button className="btn-secondary" onClick={fetchSystemInfo}>Atualizar</button>
              </div>

              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
                Selecione os documentos em formato PDF para executar a esteira didática completa. O sistema processará o layout da nota fiscal, extrairá os dados estruturados e gerará os vetores de embedding.
              </p>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                  Base / Documento Alvo:
                </label>
                <select
                  value={selectedDoc}
                  onChange={(e) => setSelectedDoc(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    marginTop: '6px',
                    borderRadius: '8px',
                    background: 'rgba(15, 23, 42, 0.8)',
                    border: '1px solid var(--border-color)',
                    color: '#FFF',
                    fontSize: '14px'
                  }}
                >
                  <option value="ALL">Todos os 4 PDFs Fictícios (Lote Completo)</option>
                  {documents.map(d => (
                    <option key={d.filename} value={d.filename}>
                      {d.filename} ({d.size_kb} KB) {d.is_indexed ? '• Já Indexado' : ''}
                    </option>
                  ))}
                </select>
              </div>

              {/* Lista dos 4 PDFs */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '24px' }}>
                {documents.map(doc => (
                  <div
                    key={doc.filename}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '10px 14px',
                      background: 'rgba(15, 23, 42, 0.5)',
                      borderRadius: '8px',
                      border: '1px solid var(--border-color)'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '13px' }}>{doc.filename}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Tamanho: {doc.size_kb} KB</div>
                    </div>
                    <span
                      style={{
                        fontSize: '11px',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontWeight: '700',
                        background: doc.is_indexed ? 'rgba(16, 185, 129, 0.15)' : 'rgba(148, 163, 184, 0.1)',
                        color: doc.is_indexed ? 'var(--accent-emerald)' : 'var(--text-muted)'
                      }}
                    >
                      {doc.is_indexed ? `${doc.chunks_count} Chunks Ativos` : 'Pendente'}
                    </span>
                  </div>
                ))}
              </div>

              <button
                className="btn-primary"
                style={{ width: '100%' }}
                onClick={handleRunIngestion}
                disabled={isIngesting}
              >
                {isIngesting ? 'Processando Pipeline RAG...' : '🚀 Executar Pipeline de Ingestão'}
              </button>
            </div>

            {/* PAINEL DIDÁTICO: RESULTADOS DO PROCESSAMENTO */}
            <div className="card-panel" style={{ maxHeight: '600px', overflowY: 'auto' }}>
              <div className="panel-header">
                <h2 className="panel-title">🔍 Rastreabilidade das Etapas</h2>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {ingestionResults ? `${ingestionResults.processed_documents_count} Docs Processados` : 'Aguardando Início'}
                </span>
              </div>

              {!ingestionResults && !isIngesting && (
                <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
                  <div style={{ fontSize: '42px', marginBottom: '12px' }}>📊</div>
                  <p>Execute a ingestão ao lado para visualizar a transformação didática dos dados em cada fase do RAG.</p>
                </div>
              )}

              {isIngesting && (
                <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                  <div className="pulse-dot" style={{ margin: '0 auto 16px auto', width: '20px', height: '20px' }}></div>
                  <p style={{ fontWeight: '600' }}>Processando pipeline na esteira...</p>
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>OCR → Chunking → FastEmbed → PGVector</p>
                </div>
              )}

              {ingestionResults && ingestionResults.results.map((res, idx) => (
                <div key={idx} style={{ marginBottom: '24px', borderBottom: '1px solid var(--border-color)', paddingBottom: '20px' }}>
                  <h3 style={{ fontSize: '15px', color: 'var(--accent-cyan)', marginBottom: '12px' }}>
                    📑 Documento: {res.document_name}
                  </h3>

                  {/* 1. Dados Estruturados */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-secondary)' }}>
                      1. Extração Estruturada (OCR / Parser):
                    </div>
                    <div style={{ fontSize: '12px', background: 'rgba(0,0,0,0.3)', padding: '10px', borderRadius: '6px', marginTop: '4px' }}>
                      <div><b>Nota:</b> {res.steps.step_1_ingestion.structured_data.invoice_number} | <b>Emissão:</b> {res.steps.step_1_ingestion.structured_data.issue_date}</div>
                      <div><b>Fornecedor:</b> {res.steps.step_1_ingestion.structured_data.provider}</div>
                      <div><b>CNPJ:</b> {res.steps.step_1_ingestion.structured_data.cnpj}</div>
                      <div><b>Total:</b> <span style={{ color: 'var(--accent-emerald)', fontWeight: 'bold' }}>{res.steps.step_1_ingestion.structured_data.total_value}</span></div>
                    </div>
                  </div>

                  {/* 2. Chunks */}
                  <div style={{ marginBottom: '14px' }}>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-secondary)' }}>
                      2. Chunks Gerados ({res.steps.step_2_chunking.total_chunks} blocos semânticos):
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '4px' }}>
                      {res.steps.step_2_chunking.chunks.map(ch => (
                        <div key={ch.chunk_index} style={{ fontSize: '11px', background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '6px', borderLeft: '3px solid var(--accent-blue)' }}>
                          <span style={{ color: 'var(--accent-blue)', fontWeight: 'bold' }}>[Chunk {ch.chunk_index} - {ch.chunk_type}]</span>
                          <div style={{ color: 'var(--text-muted)', marginTop: '2px', whiteSpace: 'pre-wrap' }}>{ch.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 3 & 4. Embeddings */}
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-secondary)' }}>
                      3 & 4. Embeddings Vetoriais (FastEmbed - 384 Dimensões):
                    </div>
                    <div style={{ fontSize: '11px', background: 'rgba(0,0,0,0.3)', padding: '8px', borderRadius: '6px', marginTop: '4px' }}>
                      {res.steps.step_4_embedding.samples.map(s => (
                        <div key={s.chunk_index} style={{ fontFamily: 'monospace', color: 'var(--accent-cyan)' }}>
                          Chunk {s.chunk_index}: [{s.embedding_sample.join(', ')} ... +376 dimensões]
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ========================================================= */}
      {/* ABA 2: CONSULTA & CHAT RAG */}
      {/* ========================================================= */}
      {activeTab === 'query' && (
        <section>
          {/* STEPPER DINÂMICO DE CONSULTA */}
          <div className="pipeline-stepper">
            <div className={`step-node ${queryActiveStep >= 1 ? 'completed' : ''} ${queryActiveStep === 1 ? 'active' : ''}`}>
              <div className="step-number">1</div>
              <div className="step-label">
                <span className="step-name">PERGUNTA</span>
                <span className="step-sub">Entrada do Usuário</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${queryActiveStep >= 2 ? 'completed' : ''} ${queryActiveStep === 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-label">
                <span className="step-name">EMBEDDING</span>
                <span className="step-sub">FastEmbed (384D)</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${queryActiveStep >= 3 ? 'completed' : ''} ${queryActiveStep === 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-label">
                <span className="step-name">RETRIEVAL</span>
                <span className="step-sub">Top-K = 5 & Scores</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${queryActiveStep >= 4 ? 'completed' : ''} ${queryActiveStep === 4 ? 'active' : ''}`}>
              <div className="step-number">4</div>
              <div className="step-label">
                <span className="step-name">PROMPT AUMENTADO</span>
                <span className="step-sub">Injeção de Contexto</span>
              </div>
            </div>
            <div className="stepper-arrow">→</div>
            <div className={`step-node ${queryActiveStep >= 5 ? 'completed' : ''} ${queryActiveStep === 5 ? 'active' : ''}`}>
              <div className="step-number">5</div>
              <div className="step-label">
                <span className="step-name">LLM RESPOSTA</span>
                <span className="step-sub">OpenRouter API</span>
              </div>
            </div>
          </div>

          <div className="chat-layout">
            {/* JANELA DO CHAT */}
            <div className="chat-main">
              <div className="messages-list">
                {chatMessages.map((msg, idx) => (
                  <div key={idx} className={`message-bubble ${msg.role}`}>
                    <div className={`avatar ${msg.role}`}>
                      {msg.role === 'user' ? 'U' : 'AI'}
                    </div>
                    <div className={`message-content ${msg.isNoContext ? 'empty-base-alert' : ''}`}>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '6px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                        {msg.time}
                      </div>
                    </div>
                  </div>
                ))}
                {isQuerying && (
                  <div className="message-bubble assistant">
                    <div className="avatar assistant">AI</div>
                    <div className="message-content">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div className="pulse-dot"></div>
                        <span>Pesquisando candidatos vetoriais e gerando resposta...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* SUGESTÕES DE PERGUNTAS RÁPIDAS */}
              <div className="quick-prompts">
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', alignSelf: 'center' }}>Testes Rápidos:</span>
                <button
                  className="quick-tag"
                  onClick={() => handleSendQuery("Qual é o valor total e o fornecedor da estação de carga rápida DC 60kW?")}
                >
                  ⚡ Estação DC 60kW & Valor
                </button>
                <button
                  className="quick-tag"
                  onClick={() => handleSendQuery("Quantos carregadores Wallbox residenciais 7.4kW foram faturados e qual a potência dos carregadores comerciais?")}
                >
                  🔋 Wallbox 7.4kW & AC 22kW
                </button>
                <button
                  className="quick-tag"
                  onClick={() => handleSendQuery("Quais materiais foram faturados para a infraestrutura de recarga no condomínio residencial?")}
                >
                  🛠️ Infraestrutura Elétrica Predial
                </button>
                <button
                  className="quick-tag"
                  onClick={() => handleSendQuery("Qual a velocidade máxima de um foguete espacial para a Lua?")}
                  style={{ borderColor: 'rgba(244, 63, 94, 0.4)', color: '#F43F5E' }}
                >
                  ⚠️ Teste Fora da Base ("Sem dados disponíveis")
                </button>
              </div>

              {/* INPUT DO CHAT */}
              <form
                className="chat-input-area"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSendQuery();
                }}
              >
                <input
                  type="text"
                  className="chat-input"
                  placeholder="Pergunte sobre modelos de carregadores, Wallbox, potência kW, valores ou instalação..."
                  value={queryInput}
                  onChange={(e) => setQueryInput(e.target.value)}
                  disabled={isQuerying}
                />
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={isQuerying || !queryInput.trim()}
                >
                  Enviar
                </button>
              </form>
            </div>

            {/* SIDEBAR DIDÁTICA: TOP_K = 5 E PROMPT AUMENTADO */}
            <div className="retrieval-sidebar">
              <div className="card-panel">
                <div className="panel-header">
                  <h3 className="panel-title" style={{ fontSize: '16px' }}>
                    🎯 Top-K = 5 Candidatos Recuperados
                  </h3>
                </div>

                {!lastQueryData && (
                  <p style={{ fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center', padding: '20px 0' }}>
                    Envie uma mensagem no chat para visualizar os 5 chunks com maiores scores de similaridade de cosseno.
                  </p>
                )}

                {lastQueryData && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {lastQueryData.steps.step_2_retrieval.candidates.map((cand, idx) => (
                      <div key={idx} className="candidate-card">
                        <div className="candidate-header">
                          <span className="candidate-badge">#{idx + 1} {cand.document_name}</span>
                          <span className="score-badge">Score: {cand.similarity_score}</span>
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--accent-cyan)', marginBottom: '4px' }}>
                          Tipo: {cand.chunk_type}
                        </div>
                        <div className="candidate-text">{cand.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* PROMPT AUMENTADO MONTADO */}
              {lastQueryData && (
                <div className="card-panel">
                  <div className="panel-header">
                    <h3 className="panel-title" style={{ fontSize: '16px' }}>
                      🧩 Prompt Aumentado (Enviado ao LLM)
                    </h3>
                  </div>
                  <pre
                    style={{
                      fontSize: '11px',
                      background: 'rgba(0, 0, 0, 0.4)',
                      padding: '12px',
                      borderRadius: '8px',
                      color: 'var(--text-secondary)',
                      whiteSpace: 'pre-wrap',
                      maxHeight: '220px',
                      overflowY: 'auto'
                    }}
                  >
                    {lastQueryData.steps.step_3_prompt_augmented.prompt_text}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </section>
      )}

      {/* ========================================================= */}
      {/* ABA 3: CONCEITOS & ARQUITETURA DIDÁTICA */}
      {/* ========================================================= */}
      {activeTab === 'architecture' && (
        <section>
          <div className="grid-3col" style={{ marginBottom: '24px' }}>
            <div className="card-panel">
              <h3 style={{ color: 'var(--accent-cyan)', marginBottom: '10px' }}>1. O que é Chunking?</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Chunking é a técnica de fatiar documentos longos em pedaços (chunks) semanticamente coesos. No nosso caso, dividimos a nota fiscal em cabeçalho, itens discriminados e totais com observações para otimizar a precisão da busca.
              </p>
            </div>

            <div className="card-panel">
              <h3 style={{ color: 'var(--accent-blue)', marginBottom: '10px' }}>2. FastEmbed & Embeddings</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                Embeddings são representações vetoriais de texto em um espaço geométrico. Utilizamos o modelo <b>sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2</b> via <b>FastEmbed</b>, que mapeia cada trecho em <b>384 dimensões</b> numéricas.
              </p>
            </div>

            <div className="card-panel">
              <h3 style={{ color: 'var(--accent-emerald)', marginBottom: '10px' }}>3. PGVector & Top-K = 5</h3>
              <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                O <b>PGVector</b> no Supabase calcula a distância de cosseno entre o vetor da pergunta e os vetores armazenados. A busca seleciona os <b>5 melhores candidatos (Top-K = 5)</b> com base no maior score de similaridade.
              </p>
            </div>
          </div>

          <div className="card-panel">
            <h2 className="panel-title" style={{ marginBottom: '16px' }}>🛡️ Segurança das Credenciais & Arquitetura</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <div>
                <h4 style={{ color: '#FFF', marginBottom: '8px' }}>Por que as chaves não vão para o Frontend?</h4>
                <p>
                  As chaves de API do Supabase e do OpenRouter permanecem isoladas no backend via variáveis do arquivo <code>.env</code>. O frontend comunica-se exclusivamente com a API REST do FastAPI, eliminando qualquer risco de vazamento de credenciais na rede ou código cliente.
                </p>
              </div>
              <div>
                <h4 style={{ color: '#FFF', marginBottom: '8px' }}>Regra "Sem dados disponíveis na base"</h4>
                <p>
                  Quando a similaridade máxima dos candidatos recuperados é inferior ao limiar mínimo ou quando nenhum item relevante é encontrado, o sistema impede alucinações e retorna com exatidão mandatória a frase: <b>"Sem dados disponíveis na base"</b>.
                </p>
              </div>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
