import requests
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

IMMICH_URL = os.getenv('IMMICH_URL', '$IMMICH_URL')
API_KEY = os.getenv('API_KEY', '$API_KEY')
ALBUM_ID = os.getenv('ALBUM_ID', '$ALBUM_ID')

DOWNLOAD_FOLDER = 'image_download'

headers = {'x-api-key': API_KEY}

def get_album_assets():

    try:
        url = f'{IMMICH_URL}/albums/{ALBUM_ID}'
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()

        album_name = response.json().get('name')

        logging.info(f"A obter assets do álbum {album_name}...")

        asset_map = {}
        for asset in response.json().get('assets', []):
            asset_id = asset.get('id')
            filename = f"{asset_id}_{asset.get('originalFileName')}"
            asset_map[asset_id] = filename

        return asset_map
    
    except requests.exceptions.RequestException as e:

        logging.error(f"Erro ao aceder à API do Immich. Verifique a chave/ID do álbum: {e}")
        return {}