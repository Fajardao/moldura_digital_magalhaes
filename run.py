
import os
import time
import updater
import downloader
import threading

TIME_TO_UPDATE_CHECK = 86400  # Verifica a cada dia
TIME_TO_SYNC = 600           # Sincroniza a cada 10 minutos
DELAY_SHOW = 10            # Segundos entre imagens

asset_map = {}
run_viewer = False
ready_to_start_sync = False
ready_to_start_view = False

def time_update():
    global ready_to_start_sync
    while True:
        if updater.is_update_needed():
            updater.perform_update()
            ready_to_start_sync = True
        else:
            ready_to_start_sync = True  # Mesmo sem update, inicia a sincronização
        time.sleep(TIME_TO_UPDATE_CHECK)  # Verifica a cada hora

def time_sync():

    global asset_map
    global run_viewer
    global ready_to_start_sync
    global ready_to_start_view

    while True:

        if ready_to_start_sync:
            asset_map2 = downloader.get_album_assets()

            print(1)

            if asset_map != asset_map2:
                print(2)
                downloader.smart_sync()
                asset_map = asset_map2
                run_viewer = False  # Reinicia o visualizador para atualizar a lista de imagens
                ready_to_start_view = True
            time.sleep(TIME_TO_SYNC)  # Sincroniza a cada 10 minutos

def view_images():
    global run_viewer
    global ready_to_start_view

    while True:
        if ready_to_start_view:
            if not run_viewer:
                run_viewer = True
                os.system("pkill feh")  # Termina instâncias existentes do feh
                time.sleep(2)  # Espera o feh terminar
                os.system(f"feh -r -z -F -D {DELAY_SHOW} {downloader.DOWNLOAD_FOLDER} &")
    

if __name__ == "__main__":
    
    update_thread = threading.Thread(target=time_update)
    sync_thread = threading.Thread(target=time_sync)
    view_thread = threading.Thread(target=view_images)

    update_thread.start()
    sync_thread.start()
    view_thread.start()

    update_thread.join()
    sync_thread.join()
    view_thread.join()

    while True:
        time.sleep(1)