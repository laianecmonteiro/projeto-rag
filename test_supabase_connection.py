import os
import sys
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

def test_supabase_connection():
    print("--- TESTE DE CONECTIVIDADE COM O SUPABASE ---")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
    
    # Validação de presença sem expor valores
    if not url:
        print("[FALHA] Variável SUPABASE_URL não configurada no arquivo .env.")
        sys.exit(1)
    if not key:
        print("[FALHA] Nenhuma chave do Supabase (SUPABASE_SECRET_KEY ou SUPABASE_PUBLISHABLE_KEY) configurada no arquivo .env.")
        sys.exit(1)
        
    print("[INFO] Variáveis de ambiente SUPABASE_URL e chave de acesso identificadas.")
    
    # Limpa possíveis espaços em branco acidentais
    url = url.strip()
    key = key.strip()

    try:
        from supabase import create_client, Client
        import httpx

        # Teste 1: Conectividade de rede/HTTP básica com o endpoint do Supabase
        health_url = f"{url}/rest/v1/"
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}"
        }
        
        response = httpx.get(health_url, headers=headers, timeout=10.0)
        
        # O Supabase REST API retorna 200 (com schema OpenAPI) quando autenticado
        if response.status_code in (200, 204):
            print(f"[SUCESSO] Comunicação HTTP estabelecida com o Supabase (Status HTTP: {response.status_code}).")
        elif response.status_code == 401:
            print(f"[FALHA] Falha de autenticação (Status HTTP 401). Verifique a validade da chave informada no .env.")
            sys.exit(1)
        else:
            print(f"[INFO] Resposta recebida do endpoint Supabase: Status HTTP {response.status_code}")

        # Teste 2: Inicialização do cliente oficial supabase-py
        client: Client = create_client(url, key)
        print("[SUCESSO] Cliente Supabase inicializado com sucesso!")
        print("---------------------------------------------")
        print("CONEXÃO COM O SUPABASE VALIDADA COM SUCESSO!")
        print("---------------------------------------------")
        return True

    except Exception as e:
        print(f"[ERRO] Ocorreu uma exceção ao conectar ao Supabase: {type(e).__name__} - {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_supabase_connection()
