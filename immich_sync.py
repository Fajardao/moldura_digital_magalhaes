import requests
import os
import glob
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# --- CONFIGURAÇÕES CRÍTICAS ---
IMMICH_URL = '$IMMICH_URL'
API_KEY = '$IMMICH_API'
ALBUM_ID = '$IMMICH_ALBUM' 
# ------------------------------

DOWNLOAD_FOLDER = 'image_download'
DOWNLOAD_ENDPOINT = 'original'
headers = {'x-api-key': API_KEY}

def get_album_assets():
    """Obtém a lista de todos os assets (fotos) no álbum do Immich."""
    logging.info(f"A obter assets do álbum {ALBUM_ID}...")
    try:
        url = f'{IMMICH_URL}/albums/{ALBUM_ID}'
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        
        album_data = response.json()
        
        # Cria um dicionário {ID_asset: Nome_do_ficheiro} para fácil consulta
        asset_map = {}
        for asset in album_data.get('assets', []):
            asset_id = asset.get('id')
            # ID é usado como prefixo para identificação local
            filename = f"{asset_id}_{asset.get('originalFileName')}"
            asset_map[asset_id] = filename
            
        return asset_map
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao aceder à API do Immich. Verifique a chave/ID do álbum: {e}")
        return {}

def download_asset(asset_id, filename):
    """Faz download de um asset individual e guarda-o localmente."""
    url = f'{IMMICH_URL}/assets/{asset_id}/{DOWNLOAD_ENDPOINT}' 
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    
    if os.path.exists(filepath):
        logging.info(f"  -> Ficheiro local '{filename}' já existe. A ignorar download.")
        return True

    logging.info(f"  -> A descarregar novo asset: {filename}...")
    try:
        # Timeout longo para o Atom N270
        response = requests.get(url, headers=headers, stream=True, verify=False, timeout=300) 
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"  -> Download concluído: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"  -> ERRO ao fazer download do asset {asset_id}: {e}")
        return False

def smart_sync_full():
    """Sincronização completa: descarrega novos e remove apagados no servidor."""
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    # 1. Obter lista de assets no Immich
    immich_assets = get_album_assets()
    immich_ids = set(immich_assets.keys())

    if not immich_ids:
        logging.warning("Nenhum asset encontrado ou erro na API. A sair do sync.")
        return

    # 2. Obter lista de assets locais
    local_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
    local_ids = set()
    local_id_to_filepath = {}
    
    for fullpath in local_files:
        filename = os.path.basename(fullpath)
        try:
            asset_id = filename.split('_')[0]
            local_ids.add(asset_id)
            local_id_to_filepath[asset_id] = fullpath
        except IndexError:
            continue 

    # --- FASE 1: DOWNLOAD/ATUALIZAÇÃO ---
    logging.info("\n--- FASE 1: Download de novos ficheiros ---")
    for asset_id, filename in immich_assets.items():
        if asset_id not in local_ids:
            download_asset(asset_id, filename)

    # --- FASE 2: LIMPEZA ---
    logging.info("\n--- FASE 2: Remoção de ficheiros apagados no servidor ---")
    for local_id in local_ids:
        if local_id not in immich_ids:
            filepath_to_delete = local_id_to_filepath[local_id]
            logging.info(f"A remover ficheiro (apagado no servidor): {os.path.basename(filepath_to_delete)}")
            os.remove(filepath_to_delete)
        
    logging.info("\nProcesso de Sincronização COMPLETA concluído.")

if __name__ == '__main__':
    smart_sync_full()