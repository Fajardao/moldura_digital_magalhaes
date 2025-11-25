import requests
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def parse_version(version_string):
    """Converte string de versão (ex: '0.9', '1.2.3') para tupla de ints para comparação."""
    try:
        return tuple(map(int, version_string.split('.')))
    except (ValueError, AttributeError):
        return (0, 0, 0)  # Versão inválida, assume 0.0.0

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
    
    local_parsed = parse_version(local_version)
    remote_parsed = parse_version(remote_version)
    
    if remote_parsed > local_parsed:
        print("UPDATE_REQUIRED")
        return True
    else:
        print("UPDATE_NOT_NEEDED")
        return False
    
def perform_update():
    """Realiza o processo de atualização."""
    logging.info("Iniciando o processo de atualização...")

    os.system("git fetch origin main")
    os.system("git reset --hard origin/main")
    os.system("git clean -fd")
    os.system("git pull origin main")

    logging.info("Atualização concluída com sucesso.")