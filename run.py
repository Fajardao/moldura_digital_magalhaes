import requests
import os
import glob

import updater
import downloder


if __name__ == "__main__":
    # Verificar se é necessária atualização
    if updater.is_update_needed():
        updater.perform_update()