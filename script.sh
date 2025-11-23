#!/bin/bash

# --- CONFIGURAÇÕES DE CONTROLO ---
PYTHON_GIT_CHECK="verify_version.py"
PYTHON_IMMICH_SYNC="immich_sync.py" 
DOWNLOAD_DIR="image_download"
UNCLUTTER_PID=""
SLIDE_DURATION=10 # Segundos por foto

# Frequência de Sincronização de Fotos (HORÁRIO)
SYNC_INTERVAL=3600 # 3600 segundos = 1 hora

# Frequência de Verificação de Código (DIÁRIO)
DAILY_COUNTER_LIMIT=24 # Número de intervalos de 1 hora num dia
GIT_CHECK_COUNTER=0    # Contador de horas (inicializado a zero)

# --- Variáveis Git ---
GIT_REPO_URL="https://github.com/Fajardao/moldura_digital_magalhaes.git"
GIT_BRANCH="main"
# ---------------------

# --- Funções de Controlo de Serviço ---

function stop_slideshow() {
    FEH_PID=$(pgrep feh)
    if [ -n "$FEH_PID" ]; then
        echo "A parar feh (PID: $FEH_PID)..."
        kill $FEH_PID 2>/dev/null
        sleep 1
    fi
}

function start_slideshow() {
    echo "A iniciar feh..."
    feh -r -z -F -D $SLIDE_DURATION "$DOWNLOAD_DIR" &
    FEH_PID=$!
}

# --- Inicialização ---
echo "--- Iniciando o Sistema de Moldura Digital (Dual-Frequência) ---"

# 1. Setup inicial e rato
xsetroot -solid black 2>/dev/null
unclutter -idle 1 &
UNCLUTTER_PID=$! 

# 2. Verificação de Versão Inicial (Garantir que corre o código mais recente no arranque)
echo "A verificar versão de código inicial..."
python3 "$PYTHON_GIT_CHECK"
if [ $? -eq 1 ]; then
    echo "NOVA VERSÃO DETETADA. A puxar e a REINICIAR SERVIÇO."
    stop_slideshow
    git pull origin $GIT_BRANCH
    exit 0 
fi

# 3. Sincronização inicial (Garantir que há fotos)
python3 "$PYTHON_IMMICH_SYNC"

if [ ! -d "$DOWNLOAD_DIR" ] || [ -z "$(ls -A "$DOWNLOAD_DIR" 2>/dev/null)" ]; then
    echo "ERRO: Pasta de download vazia. A sair."
    kill $UNCLUTTER_PID 2>/dev/null
    exit 1
fi

# 4. Iniciar o slideshow inicial
start_slideshow

# --- Loop de Controlo Diário e Horário ---
while true; do
    
    echo "A dormir por $SYNC_INTERVAL segundos (1 hora)..."
    sleep $SYNC_INTERVAL
    
    # 1. Incrementa o contador de horas
    GIT_CHECK_COUNTER=$((GIT_CHECK_COUNTER + 1))
    
    # 2. SE FOR HORA DE VERIFICAR O CÓDIGO (A CADA 24 HORAS)
    if [ $GIT_CHECK_COUNTER -ge $DAILY_COUNTER_LIMIT ]; then
        echo "--- INÍCIO DA VERIFICAÇÃO DIÁRIA DE CÓDIGO ---"
        
        # Parar o slideshow para executar a verificação
        stop_slideshow 
        
        python3 "$PYTHON_GIT_CHECK"
        if [ $? -eq 1 ]; then
            echo "NOVA VERSÃO DETETADA. A puxar e REINICIAR o serviço."
            git pull origin $GIT_BRANCH
            exit 0 # Sai para carregar o novo código
        fi
        
        GIT_CHECK_COUNTER=0
        echo "--- FIM DA VERIFICAÇÃO DIÁRIA ---"
    fi
    
    # 3. SINCRONIZAÇÃO DE FOTOS (HORÁRIA)
    # Esta sincronização ocorre a cada hora.
    stop_slideshow # Parar feh para permitir o sync de ficheiros
    python3 "$PYTHON_IMMICH_SYNC"
    
    # 4. Reiniciar feh para carregar as novas fotos
    start_slideshow
    
done

# --- Ponto de Saída (CTRL+C) ---
stop_slideshow
kill $UNCLUTTER_PID 2>/dev/null

echo "--- Script concluído. ---"