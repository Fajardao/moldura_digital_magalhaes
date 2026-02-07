
import os
import sys
import time
import updater
import downloader
import threading
#import usb_watcher

TIME_TO_UPDATE_CHECK = 86400  # Verifica a cada dia
TIME_TO_SYNC = 600           # Sincroniza a cada 10 minutos
DELAY_SHOW = 10            # Segundos entre imagens

asset_map = {}
run_viewer = False
ready_to_start_sync = False
ready_to_start_view = False

kill=False
restart_needed = False

def time_update():
    global kill
    global restart_needed
    global ready_to_start_sync
    while True:
        if updater.is_update_needed():
            updater.perform_update()
            print("Update completed, restart needed")
            restart_needed = True
            kill = True
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

            if asset_map != asset_map2:
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

#def watch_usb_thread():
#    """Thread para monitorizar dispositivos USB e fazer upload automático."""
#    usb_watcher.watch_and_upload()

    

if __name__ == "__main__":
    
    update_thread = threading.Thread(target=time_update, daemon=True)
    sync_thread = threading.Thread(target=time_sync, daemon=True)
    view_thread = threading.Thread(target=view_images, daemon=True)
    #usb_thread = threading.Thread(target=watch_usb_thread, daemon=True)

    update_thread.start()
    sync_thread.start()
    view_thread.start()
    #usb_thread.start()

    try:
        while True:
            time.sleep(1)
            if kill:
                print("Terminando processo principal...")
                if restart_needed:
                    print("Reiniciando aplicação...")
                    # Re-executa o script Python
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                else:
                    sys.exit(0)
    except KeyboardInterrupt:
        print("Interrupção do utilizador, encerrando...")
        sys.exit(0)