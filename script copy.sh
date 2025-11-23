#!/bin/bash

# --- Configurações ---
PYTHON_SYNC_SCRIPT="immich_sync.py" 
DOWNLOAD_DIR="image_download"
UNCLUTTER_PID=""
SLIDE_DURATION=10 # Segundos por foto
SYNC_INTERVAL=3600 # 3600 segundos = 1 hora
# ---------------------

# --- Funções de Controlo ---

function start_slideshow() {
    echo "A iniciar feh..."
    # As opções -r, -z, -F, -D e --auto-reload são as mais adequadas.
    # O comando & envia feh para o background, e guardamos o PID.
    feh -r -Z -F -D $SLIDE_DURATION "$DOWNLOAD_DIR" &
    FEH_PID=$!
}

function stop_slideshow() {
    if [ -n "$FEH_PID" ]; then
        echo "A parar feh (PID: $FEH_PID)..."
        kill $FEH_PID 2>/dev/null
        # Pausa para garantir que o processo termina
        sleep 1
    fi
}

function run_sync() {
    echo "--- INÍCIO DA SINCRONIZAÇÃO HORÁRIA ---"
    python3 "$(dirname "$0")/$PYTHON_SYNC_SCRIPT"
    echo "--- SINCRONIZAÇÃO CONCLUÍDA ---"
}

# --- Inicialização ---
echo "--- Iniciando o Sistema de Moldura Digital (Modo Horário) ---"

# 1. Setup inicial
xsetroot -solid black 2>/dev/null
unclutter -idle 1 &
UNCLUTTER_PID=$! 

# 2. Sincronização inicial para garantir que há fotos
run_sync

if [ ! -d "$DOWNLOAD_DIR" ] || [ -z "$(ls -A "$DOWNLOAD_DIR" 2>/dev/null)" ]; then
    echo "ERRO: Pasta de download vazia. Verifique o seu ALBUM_ID e API Key."
    exit 1
fi

# 3. Iniciar o slideshow inicial
start_slideshow

# --- Loop de Controlo Horário ---
while true; do
    
    echo "A dormir por $SYNC_INTERVAL segundos (1 hora)..."
    sleep $SYNC_INTERVAL
    
    # Reinicia o ciclo de atualização:
    
    # 1. Parar o feh para libertar a pasta e permitir a sincronização
    stop_slideshow
    
    # 2. Executar a sincronização (descarrega e apaga)
    run_sync
    
    # 3. Reiniciar feh para carregar as novas fotos
    start_slideshow
    
done

# --- APLICAÇÃO DE CONTROLO ---
# Este ponto só é atingido se o utilizador fechar o feh e o script
stop_slideshow
kill $UNCLUTTER_PID 2>/dev/null

echo "--- Script concluído. ---"