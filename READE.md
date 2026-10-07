# ⚡ RAG Laiane - Pipeline Didático de Veículos Elétricos

Sistema completo e didático de **RAG (Retrieval-Augmented Generation)** voltado à gestão e consulta inteligente de notas fiscais e equipamentos de infraestrutura para **veículos elétricos (VEs)**.

---

## 🛠️ Procedimento de Instalação e Ambiente Virtual

### 1. Criar o Ambiente Virtual (`venv`)
```bash
python -m venv venv
```

### 2. Ativar o Ambiente Virtual
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Se necessário, libere a política de execução: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

* **Windows (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```

* **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Instalar as Dependências do `requirements.txt` / `requeriments.txt`
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

Para a documentação completa da arquitetura, execução dos servidores e testes do chat, consulte o arquivo oficial [README.md](README.md).
