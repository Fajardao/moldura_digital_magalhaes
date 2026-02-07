

import logging
import os
import time

import requests


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

IMMICH_URL = os.getenv('IMMICH_URL', '$IMMICH_URL')
API_KEY = os.getenv('API_KEY', '$API_KEY')
ALBUM_ID = os.getenv('ALBUM_ID', '$ALBUM_ID')

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.raw'}

headers = {'x-api-key': API_KEY}

def get_mounted_usb_devices():

    try:
        usb_devices = {}
        media_dirs = ['/mnt', '/media']

        for media_dir in media_dirs:
            if os.path.exists(media_dir):
                for entry in os.scandir(media_dir):
                    if entry.is_dir():
                        usb_devices[entry.path] = entry.name

        return usb_devices

    except Exception as e:
        logging.error(f"Erro ao detectar dispositivos USB: {e}")
        return {}
    
def upload_images_from_usb(mount_point):

    try:
        logging.info(f"A verificar imagens no dispositivo USB montado em {mount_point}...")

        for root, _, files in os.walk(mount_point):
            for file in files:
                if os.path.splitext(file)[1].lower() in IMAGE_EXTENSIONS:
                    filepath = os.path.join(root, file)
                    logging.info(f"  -> A carregar imagem: {filepath}")
                    try:
                        mtime = os.path.getmtime(filepath)
                        ctime = os.path.getctime(filepath)
                    except Exception:
                        mtime = None
                        ctime = None

                    from datetime import datetime
                    file_modified_iso = datetime.fromtimestamp(mtime).isoformat() if mtime else None
                    file_created_iso = datetime.fromtimestamp(ctime).isoformat() if ctime else None

                    with open(filepath, 'rb') as f:
                        files = {'assetData': (file, f, 'application/octet-stream')}
                        data = {'filename': file}
                        if file_created_iso:
                            data['fileCreatedAt'] = file_created_iso
                        if file_modified_iso:
                            data['fileModifiedAt'] = file_modified_iso

                        url = f'{IMMICH_URL}/assets'
                        response = requests.post(url, headers=headers, files=files, data=data, verify=False, timeout=300)
                        if response.status_code >= 400:
                            logging.error(f"Upload falhou ({response.status_code}) para {filepath}: {response.text}")
                            continue
                        response.raise_for_status()
                    logging.info(f"  -> Upload concluído: {file}")

        logging.info(f"Upload de imagens do dispositivo USB em {mount_point} concluído.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao fazer upload para o Immich: {e}")
    except Exception as e:
        logging.error(f"Erro ao processar imagens do USB: {e}")

def watch_and_upload():

    already_processed = set()

    while True:
        usb_devices = get_mounted_usb_devices()

        for mount_point, device_name in usb_devices.items():
            if mount_point not in already_processed:
                logging.info(f"Dispositivo USB detectado: {device_name} em {mount_point}")
                upload_images_from_usb(mount_point)
                already_processed.add(mount_point)

        time.sleep(30)  # Verifica a cada 30 segundos

