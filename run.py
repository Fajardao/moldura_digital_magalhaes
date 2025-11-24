
import os

import updater
import downloader


if __name__ == "__main__":
    # Verificar se é necessária atualização
    if updater.is_update_needed():
        updater.perform_update()