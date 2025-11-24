#!/bin/bash

CONFIG_FILE="data.sh"

function get_config() {
    # Inicializa variáveis com valores vazios
    IMMICH_URL=""
    IMMICH_PORT=""
    API_KEY=""
    ALBUM_ID=""


    # Tenta obter a URL do Immich
    IMMICH_URL=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "IP do servidor Immich" 10 60 "$IMMICH_URL" 2>&1 >/dev/tty)
    
    if [ $? -ne 0 ]; then return 1; fi # Sair se o utilizador cancelar

    IMMICH_PORT=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "Porta do Servidor Immich" 10 60 "$IMMICH_PORT" 2>&1 >/dev/tty)
    
    if [ $? -ne 0 ]; then return 1; fi # Sair se o utilizador cancelar

    # Tenta obter a Chave API
    API_KEY=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "Chave API do Immich (VjiJvripKDXBgr...)" 10 60 "$API_KEY" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Tenta obter o ID do Álbum
    ALBUM_ID=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "ID do Álbum Dedicado (Ex: 9b2b8d46-12f4-42b5-8f69-37140bc4430f)" 10 60 "$ALBUM_ID" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Confirmação Final
    dialog --title "CONFIRMAÇÃO" --yesno "Tem certeza que as informações estão corretas?\n\nURL: $IMMICH_URL\nAPI: $API_KEY (parcial)\nALBUM: $ALBUM_ID" 15 60
    if [ $? -ne 0 ]; then get_config; fi # Se for Não, recomeça

    # Salva no ficheiro de configuração
    save_config
}

function save_config() {
    echo "#!/bin/bash" > "$CONFIG_FILE"
    echo "# Ficheiro de configurações gerado pelo setup_magalhaes.sh" >> "$CONFIG_FILE"
    echo "IMMICH_URL=\"$IMMICH_URL:$IMMICH_PORT/api\"" >> "$CONFIG_FILE"
    echo "API_KEY=\"$API_KEY\"" >> "$CONFIG_FILE"
    echo "ALBUM_ID=\"$ALBUM_ID\"" >> "$CONFIG_FILE"
    
    chmod +x "$CONFIG_FILE"

    ./"$CONFIG_FILE"
    
    dialog --title "SUCESSO" --msgbox "Configurações guardadas em '$CONFIG_FILE'.\nPronto para iniciar o serviço." 10 60
}

# Verifica se o ficheiro de configuração já existe
if [ -f "$CONFIG_FILE" ]; then
    dialog --title "FICHEIRO EXISTENTE" --yesno "O ficheiro '$CONFIG_FILE' já existe. Deseja reconfigurar e sobrescrever?" 10 60
    if [ $? -ne 0 ]; then 
        echo "ICANCELADO PELO UTILIZADOR. A SAIR."
        exit 0
    fi
fi

# Inicia a recolha de dados
get_config

# Clona os ficheiros necessários
get_files

# --- 3. FINALIZAÇÃO ---
echo "As configurações foram guardadas em '$CONFIG_FILE'."