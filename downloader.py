import requests
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

IMMICH_URL = os.getenv('IMMICH_URL', '$IMMICH_URL')
API_KEY = os.getenv('IMMICH_API', '$IMMICH_API')
ALBUM_ID = os.getenv('IMMICH_ALBUM', '$IMMICH_ALBUM')

print(f"IMMICH_URL: {IMMICH_URL}")
print(f"API_KEY: {API_KEY}")
print(f"ALBUM_ID: {ALBUM_ID}")  