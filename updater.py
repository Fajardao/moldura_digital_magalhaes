import requests
import os
import logging

def get_remote_version():
    """Obtém o conteúdo do ficheiro 'version' diretamente da API do GitHub."""
    
    url = f"https://raw.githubusercontent.com/Fajardao/moldura_digital_magalhaes/main/version"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() 
        return response.text.strip()
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Falha ao aceder ao repositório para verificação de versão. {e}")
        return None
    
def get_local_version():
    """Lê a versão local."""
    if os.path.exists("version"):
        with open("version", 'r') as f:
            return f.read().strip()
    return "0.0.0"

def is_update_needed():
    """Verifica se é necessário atualizar comparando a versão local com a remota."""
    local_version = get_local_version()
    remote_version = get_remote_version()
    
    if remote_version is None:
        return False  # Não faz nada se falhar a verificação
    
    if remote_version > local_version:
        print("UPDATE_REQUIRED")
        return True
    else:
        print("UPDATE_NOT_NEEDED")
        return False
    
def perform_update():
    """Realiza o processo de atualização."""
    logging.info("Iniciando o processo de atualização...")

    os.system("git fetch origin main")
    os.system("git pull origin main")

    logging.info("Atualização concluída com sucesso.")