#!/bin/bash

# Este script utiliza o 'dialog' para recolher as configurações do Immich e do Git.

CONFIG_FILE="config.sh"
REQUIRED_PACKAGES="dialog git python3-pip"

# --- 1. FUNÇÕES ---

function check_dependencies() {
    echo "A verificar dependências..."
    
    # Verifica a existência dos pacotes requeridos
    for pkg in $REQUIRED_PACKAGES; do
        if ! command -v "$pkg" &> /dev/null; then
            dialog --title "DEPENDÊNCIAS EM FALTA" --msgbox "O pacote '$pkg' é necessário. Por favor, instale-o com 'sudo apt install $pkg' antes de continuar." 10 60
            exit 1
        fi
    done
}

function get_config() {
    # Inicializa variáveis com valores vazios
    IMMICH_URL=""
    API_KEY=""
    ALBUM_ID=""
    GITHUB_USER=""
    GITHUB_REPO=""

    # Tenta obter a URL do Immich
    IMMICH_URL=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "Endereço Base da API Immich (Ex: http://192.168.1.102:2283/api)" 10 60 "$IMMICH_URL" 2>&1 >/dev/tty)
    
    if [ $? -ne 0 ]; then return 1; fi # Sair se o utilizador cancelar

    # Tenta obter a Chave API
    API_KEY=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "Chave API do Immich (VjiJvripKDXBgr...)" 10 60 "$API_KEY" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Tenta obter o ID do Álbum
    ALBUM_ID=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "ID do Álbum Dedicado (Ex: 9b2b8d46-12f4-42b5-8f69-37140bc4430f)" 10 60 "$ALBUM_ID" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Tenta obter o Utilizador GitHub
    GITHUB_USER=$(dialog --title "CONFIGURAÇÃO GIT" \
        --inputbox "Nome de Utilizador/Organização do Repositório GitHub" 10 60 "$GITHUB_USER" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Tenta obter o Nome do Repositório GitHub
    GITHUB_REPO=$(dialog --title "CONFIGURAÇÃO GIT" \
        --inputbox "Nome do Repositório GitHub (Ex: magalhaes-frame)" 10 60 "$GITHUB_REPO" 2>&1 >/dev/tty)

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
    echo "IMMICH_URL=\"$IMMICH_URL\"" >> "$CONFIG_FILE"
    echo "API_KEY=\"$API_KEY\"" >> "$CONFIG_FILE"
    echo "ALBUM_ID=\"$ALBUM_ID\"" >> "$CONFIG_FILE"
    echo "GITHUB_USER=\"$GITHUB_USER\"" >> "$CONFIG_FILE"
    echo "GITHUB_REPO=\"$GITHUB_REPO\"" >> "$CONFIG_FILE"
    echo "GIT_BRANCH=\"main\"" >> "$CONFIG_FILE"
    echo "VERSION_FILE_PATH=\"version\"" >> "$CONFIG_FILE"
    
    chmod +x "$CONFIG_FILE"
    
    dialog --title "SUCESSO" --msgbox "Configurações guardadas em '$CONFIG_FILE'.\nPronto para iniciar o serviço." 10 60
}

# --- 2. EXECUÇÃO ---

# Verifica se o dialog está instalado e outras dependências
check_dependencies

# Verifica se o ficheiro de configuração já existe
if [ -f "$CONFIG_FILE" ]; then
    dialog --title "FICHEIRO EXISTENTE" --yesno "O ficheiro '$CONFIG_FILE' já existe. Deseja reconfigurar e sobrescrever?" 10 60
    if [ $? -ne 0 ]; then 
        echo "Instalação cancelada. Utilize o ficheiro existente."
        exit 0
    fi
fi

# Inicia a recolha de dados
get_config

# --- 3. FINALIZAÇÃO ---
echo "Instalação concluída. As configurações foram guardadas em '$CONFIG_FILE'."