import requests
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- CONFIGURAÇÕES DE REPOSITÓRIO (GIT) ---
GITHUB_USER = "Fajardao"
GITHUB_REPO = "moldura_digital_magalhaes"
VERSION_FILE_PATH = "version"
BRANCH = "main"                      
LOCAL_VERSION_PATH = "version" 
# ----------------------------------------

def get_remote_version():
    """Obtém o conteúdo do ficheiro 'version' diretamente da API do GitHub."""
    
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/{VERSION_FILE_PATH}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.text.strip()
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao aceder ao repositório para verificação de versão. {e}")
        return None

def get_local_version():
    """Lê a versão local."""
    if os.path.exists(LOCAL_VERSION_PATH):
        with open(LOCAL_VERSION_PATH, 'r') as f:
            return f.read().strip()
    return "0.0.0"

if __name__ == "__main__":
    local_version = get_local_version()
    remote_version = get_remote_version()
    
    if remote_version is None:
        exit(0) # Não faz nada se falhar a verificação
    
    if remote_version > local_version:
        print("UPDATE_REQUIRED")
        exit(1) # Código de saída 1 para indicar que é preciso atualizar
    else:
        print("UPDATE_NOT_NEEDED")
        exit(0)