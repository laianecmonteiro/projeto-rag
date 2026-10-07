# ⚡ RAG Laiane - Pipeline Didático de Veículos Elétricos

Sistema completo e didático de **RAG (Retrieval-Augmented Generation)** voltado à gestão e consulta inteligente de notas fiscais e equipamentos de infraestrutura para **veículos elétricos (VEs)** — incluindo carregadores residenciais Wallbox 7.4kW, estações de recarga ultrarrápida DC 60kW, cabos Tipo 2 e serviços de adequação elétrica predial.

---

## 🎯 Objetivo Didático

Este projeto foi construído para demonstrar, de forma transparente e rastreável, cada etapa de um pipeline moderno de RAG sem abstrações ocultas:

1. **Ingestão & Extração**: leitura estruturada de documentos fiscais em PDF e organização tabular com Pandas.
2. **Chunking Semântico**: segmentação intencional em blocos contextuais (Cabeçalho/Fornecedor, Itens/Produtos, Totais/Observações).
3. **Tokenização**: contagem e análise dos tokens do texto.
4. **Embeddings Locais com FastEmbed**: geração de vetores semânticos com o modelo multilíngue `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (**384 dimensões**).
5. **Armazenamento Vetorial (PGVector)**: persistência dos vetores no Supabase / PostgreSQL.
6. **Retrieval**: busca por similaridade de cosseno com **Top-K = 5** e exibição dos scores numéricos.
7. **Prompt Aumentado**: injeção restrita do contexto recuperado no prompt.
8. **LLM (OpenRouter)**: geração da resposta final fundamentada exclusivamente nos dados recuperados.
9. **Prevenção de Alucinações**: resposta estrita **`"Sem dados disponíveis na base"`** caso a pergunta fuja dos dados existentes.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia | Função |
| :--- | :--- | :--- |
| **Frontend** | Next.js (App Router, Vanilla CSS) | Interface moderna, chat interativo e esteiras visuais |
| **Backend** | Python 3.12 (FastAPI, Uvicorn) | APIs REST, regras de negócio e controle do pipeline |
| **Embeddings** | FastEmbed (Qdrant ONNX) | Geração rápida de vetores sem dependências pesadas |
| **Banco Vetorial** | Supabase (PostgreSQL + PGVector) | Armazenamento relacional e busca vetorial de cosseno |
| **LLM Provider** | OpenRouter (`openrouter/auto`) | Roteamento dinâmico para modelos de linguagem de ponta |
| **Processamento PDF** | ReportLab & PDFPlumber | Geração de PDFs e extração precisa de tabelas |
| **Estruturação Tabular**| Pandas | Normalização e estruturação dos campos das notas |

---

## 📂 Estrutura do Repositório

```text
├── data/
│   └── invoices/                     # 4 PDFs de notas fiscais fictícias de VEs
│       ├── NF_001_VoltCharge_Equipamentos.pdf
│       ├── NF_002_FastEletro_EstacoesDC.pdf
│       ├── NF_003_SolarPower_Instalacao.pdf
│       └── NF_004_EcoMobility_Servicos.pdf
├── frontend/                         # Aplicação Next.js
│   ├── src/
│   │   └── app/
│   │       ├── globals.css           # Design system (Dark mode, glassmorphism)
│   │       ├── layout.js             # Layout e metadados da aplicação
│   │       └── page.js               # Interface completa de Ingestão e Chat RAG
│   └── package.json
├── generate_invoices.py              # Script gerador dos PDFs fictícios de teste
├── rag_pipeline.py                   # Pipeline central (Extração, Chunks, FastEmbed, Retrieval)
├── server.py                         # Servidor FastAPI com endpoints REST
├── schema.sql                        # Script SQL para criação da tabela e função RPC no PGVector
├── test_supabase_connection.py       # Teste isolado e seguro de conexão com o Supabase
├── test_rag_flow.py                  # Teste automatizado ponta a ponta do fluxo RAG
├── requirements.txt                  # Dependências Python do backend
├── .env.example                      # Modelo seguro de variáveis de ambiente
├── .gitignore                        # Proteção contra envio de arquivos desnecessários e .env
└── README.md                         # Documentação completa do projeto
```

---

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
- **Python 3.12** instalado.
- **Node.js** (v18+) e **npm** instalados.

### 2. Criação do Ambiente Virtual (`venv`) e Instalação de Pacotes

O uso de um ambiente virtual (**venv**) garante que as bibliotecas do projeto fiquem isoladas, evitando conflitos com outras versões de pacotes do sistema operacional.

#### Passo 2.1: Criar o Ambiente Virtual
Abra o terminal na pasta raiz do projeto (`rag/`) e execute:
```bash
python -m venv venv
```
> *Esse comando cria o diretório `venv/`, contendo uma cópia isolada do interpretador Python e do gerenciador de pacotes `pip`.*

---

#### Passo 2.2: Ativar o Ambiente Virtual
A ativação direciona o terminal para utilizar os executáveis e pacotes isolados do `venv`. Escolha o comando de acordo com o seu sistema operacional/terminal:

* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Caso ocorra erro de política de execução de scripts no PowerShell, execute primeiro: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` e tente ativar novamente).*

* **Windows (Prompt de Comando - CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```

* **Linux / macOS (Bash / Zsh):**
  ```bash
  source venv/bin/activate
  ```

> **Como confirmar que está ativo:** Você verá o prefixo `(venv)` antes da linha de comando no terminal, como por exemplo: `(venv) PS C:\Users\...\rag>`.

---

#### Passo 2.3: Atualizar o Gerenciador de Pacotes (`pip`)
Recomenda-se atualizar o `pip` para garantir compatibilidade com as versões mais recentes das rodas (wheels):
```bash
python -m pip install --upgrade pip
```

---

#### Passo 2.4: Instalar os Pacotes do `requirements.txt`
Com o ambiente ativado, instale todas as dependências do projeto executando:
```bash
pip install -r requirements.txt
```
*(Também é possível executar `pip install -r requeriments.txt`)*

**Para verificar se todos os pacotes foram instalados com sucesso:**
```bash
pip list
```
Deverão constar pacotes como `fastapi`, `uvicorn`, `fastembed`, `supabase`, `pandas`, `pdfplumber`, entre outros.

### 3. Variáveis de Ambiente
Copie o arquivo modelo e preencha suas chaves no `.env`:
```bash
cp .env.example .env
```
Campos necessários:
- `SUPABASE_URL`: URL do seu projeto Supabase.
- `SUPABASE_SECRET_KEY`: Chave de serviço ou API key do Supabase.
- `OPENROUTER_API_KEY`: Chave de acesso à API do OpenRouter.

### 4. Teste Isolado de Conectividade com o Supabase
Antes de subir a aplicação, execute o teste de validação:
```bash
python test_supabase_connection.py
```

### 5. Gerar os 4 PDFs de Notas Fiscais Fictícias
```bash
python generate_invoices.py
```

### 6. Iniciar o Backend FastAPI
```bash
python server.py
# O backend estará disponível em: http://localhost:8000
# Documentação Swagger interativa: http://localhost:8000/docs
```

### 7. Iniciar o Frontend Next.js
Em outro terminal:
```bash
cd frontend
npm install
npm run dev
# Acesse no navegador: http://localhost:3000
```

---

## 🧪 Exemplos de Perguntas para Teste no Chat

1. **Consulta de Equipamento & Fornecedor**:
   - *"Qual é o valor total e o fornecedor da estação de carga rápida DC 60kW?"*
   - *(Recupera NF-002389 da FastEletro no valor de R$ 78.000,00).*
2. **Consulta de Quantidade e Potência**:
   - *"Quantos carregadores Wallbox residenciais 7.4kW foram faturados e qual a potência dos carregadores comerciais?"*
   - *(Recupera 5 unidades Wallbox 7.4kW e modelo AC 22kW da VoltCharge).*
3. **Consulta de Infraestrutura Predial**:
   - *"Quais materiais foram faturados para a infraestrutura de recarga no condomínio residencial?"*
   - *(Recupera Transformador 75kVA, Quadros com DPS e cabos 35mm²).*
4. **Teste de Ausência de Dados (Prevenção de Alucinações)**:
   - *"Qual a velocidade máxima de um foguete espacial para a Lua?"*
   - **Retorno Obrigatório:** `"Sem dados disponíveis na base"`.

---

## 🔒 Boas Práticas de Segurança

- As credenciais de API do Supabase e OpenRouter permanecem exclusivamente no backend e são carregadas do arquivo `.env`.
- O frontend Next.js interage com o backend via proxy de API REST, sem acesso a nenhuma chave remota.
- O arquivo `.gitignore` previne o envio acidental de arquivos `.env`, diretórios `venv/`, `node_modules/` e artefatos de build.
