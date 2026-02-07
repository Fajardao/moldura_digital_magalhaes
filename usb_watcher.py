import os
import logging
import subprocess
import time
import requests
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

IMMICH_URL = os.getenv('IMMICH_URL', '$IMMICH_URL')
API_KEY = os.getenv('API_KEY', '$API_KEY')
ALBUM_ID = os.getenv('ALBUM_ID', '$ALBUM_ID')

# Extensões de imagem suportadas
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.raw'}

headers = {'x-api-key': API_KEY}


def get_mounted_usb_devices():
    """
    Obtém lista de dispositivos USB montados em /mnt ou /media.
    Retorna dicionário com mount_point: device_info
    """
    try:
        # Executa 'lsblk -J' para obter info de dispositivos em JSON
        result = subprocess.run(['lsblk', '-J'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            logging.warning("Falha ao executar lsblk")
            return {}
        
        import json
        data = json.loads(result.stdout)
        
        usb_devices = {}
        for blockdevice in data.get('blockdevices', []):
            # Procura dispositivos USB (ttype == 'disk' e subsystems contém 'usb')
            if _is_usb_device(blockdevice):
                mount_point = _get_mount_point(blockdevice)
                if mount_point and os.path.ismount(mount_point):
                    usb_devices[mount_point] = blockdevice.get('name', 'unknown')
        
        return usb_devices
    
    except Exception as e:
        logging.error(f"Erro ao detectar dispositivos USB: {e}")
        return {}


def _is_usb_device(blockdevice):
    """Verifica se o dispositivo é USB baseado em info do lsblk."""
    try:
        # Verifica se tem subsistemas USB
        if 'usb' in str(blockdevice.get('subsystems', '')).lower():
            return True
    except:
        pass
    return False


def _get_mount_point(blockdevice):
    """Extrai o mount_point do primeiro volume montado do dispositivo."""
    try:
        children = blockdevice.get('children', [])
        for child in children:
            mount_point = child.get('mountpoint')
            if mount_point:
                return mount_point
    except:
        pass
    return None


def find_images_in_path(path):
    """Procura recursivamente ficheiros de imagem num caminho."""
    images = []
    try:
        path_obj = Path(path)
        for file in path_obj.rglob('*'):
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
                images.append(str(file))
    except Exception as e:
        logging.error(f"Erro ao procurar imagens em {path}: {e}")
    
    return images


def upload_image_to_immich(file_path):
    """
    Faz upload de uma imagem para o Immich.
    Adiciona à album especificada se estiver configurado.
    """
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            url = f'{IMMICH_URL}/assets'
            
            response = requests.post(url, headers=headers, files=files, verify=False, timeout=60)
            response.raise_for_status()
            
            asset_data = response.json()
            asset_id = asset_data.get('id')
            
            if asset_id and ALBUM_ID:
                # Adiciona a asset ao album
                add_to_album(asset_id)
            
            logging.info(f"Upload concluído: {os.path.basename(file_path)} (ID: {asset_id})")
            return True
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao fazer upload de {file_path}: {e}")
        return False
    except Exception as e:
        logging.error(f"Erro inesperado ao fazer upload: {e}")
        return False


def add_to_album(asset_id):
    """Adiciona um asset ao album especificado."""
    try:
        url = f'{IMMICH_URL}/albums/{ALBUM_ID}/assets'
        payload = {'ids': [asset_id]}
        
        response = requests.put(url, headers=headers, json=payload, verify=False, timeout=10)
        response.raise_for_status()
        
        logging.info(f"Asset adicionado ao album {ALBUM_ID}")
        return True
    
    except Exception as e:
        logging.error(f"Erro ao adicionar asset ao album: {e}")
        return False


def watch_and_upload():
    """
    Monitora dispositivos USB e faz upload de imagens quando detecta novos ficheiros.
    """
    logged_devices = set()
    processed_files = set()
    
    while True:
        try:
            usb_devices = get_mounted_usb_devices()
            
            current_devices = set(usb_devices.keys())
            
            # Detecta novos dispositivos
            new_devices = current_devices - logged_devices
            if new_devices:
                for device in new_devices:
                    logging.info(f"Dispositivo USB detectado: {device}")
                    logged_devices.add(device)
            
            # Detecta dispositivos removidos
            removed_devices = logged_devices - current_devices
            if removed_devices:
                for device in removed_devices:
                    logging.info(f"Dispositivo USB removido: {device}")
                    logged_devices.discard(device)
            
            # Processa imagens em dispositivos montados
            for mount_point in usb_devices.keys():
                images = find_images_in_path(mount_point)
                
                for image_path in images:
                    if image_path not in processed_files:
                        logging.info(f"Imagem encontrada em USB: {image_path}")
                        if upload_image_to_immich(image_path):
                            processed_files.add(image_path)
                            time.sleep(2)  # Pequeno delay entre uploads
        
        except Exception as e:
            logging.error(f"Erro geral no watch_and_upload: {e}")
        
        time.sleep(5)  # Verifica a cada 5 segundos


if __name__ == "__main__":
    logging.info("Iniciando monitor de USB...")
    watch_and_upload()
