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
        --inputbox "Chave API do Immich" 10 60 "$API_KEY" 2>&1 >/dev/tty)

    if [ $? -ne 0 ]; then return 1; fi

    # Tenta obter o ID do Álbum
    ALBUM_ID=$(dialog --title "CONFIGURAÇÃO IMMICH" \
        --inputbox "ID do Álbum Dedicado" 10 60 "$ALBUM_ID" 2>&1 >/dev/tty)

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
    echo "export IMMICH_URL=\"$IMMICH_URL:$IMMICH_PORT/api\"" >> "$CONFIG_FILE"
    echo "export API_KEY=\"$API_KEY\"" >> "$CONFIG_FILE"
    echo "export ALBUM_ID=\"$ALBUM_ID\"" >> "$CONFIG_FILE"
    
    chmod +x "$CONFIG_FILE"

    # Carrega as variáveis no ambiente desta shell (não no shell pai).
    . "$CONFIG_FILE"
    
    dialog --title "SUCESSO" --msgbox "Configurações guardadas em '$CONFIG_FILE'.\nPronto para iniciar o serviço." 10 60
}

function persist_env_vars() {
    # Apenas para Debian: grava em ~/.profile (usuário) ou em /etc/profile.d/ (system-wide, requer sudo)
    dialog --title "VARIÁVEIS DE AMBIENTE" --yesno "Deseja gravar as variáveis como variáveis de ambiente permanentes no sistema (Debian)?\n(Isto afetará apenas novos terminais/sessões)" 10 70
    if [ $? -ne 0 ]; then return 0; fi

    if [ -f /etc/debian_version ]; then
        dialog --title "GRAVAR SISTEMA" --yesno "Gravar system-wide em /etc/profile.d/ (requer sudo)?\nEscolha 'Não' para gravar apenas no ~/.profile (apenas para este utilizador)." 10 70
        if [ $? -eq 0 ]; then
            tmpfile=$(mktemp)
            cat > "$tmpfile" <<EOF
export IMMICH_URL="${IMMICH_URL}:${IMMICH_PORT}/api"
export API_KEY="${API_KEY}"
export ALBUM_ID="${ALBUM_ID}"
EOF
            if command -v sudo >/dev/null 2>&1; then
                sudo mv "$tmpfile" /etc/profile.d/moldura_magalhaes.sh
                sudo chmod 644 /etc/profile.d/moldura_magalhaes.sh
                dialog --title "SUCESSO" --msgbox "Variáveis gravadas em /etc/profile.d/moldura_magalhaes.sh. Abra uma nova sessão para as ver." 10 70
            else
                # fallback para user profile se não houver sudo
                cat "$tmpfile" >> ~/.profile
                rm -f "$tmpfile"
                dialog --title "SUCESSO" --msgbox "Não encontrei 'sudo'. Adicionadas variáveis a ~/.profile." 10 70
            fi
        else
            echo "export IMMICH_URL=\"${IMMICH_URL}:${IMMICH_PORT}/api\"" >> ~/.profile
            echo "export API_KEY=\"${API_KEY}\"" >> ~/.profile
            echo "export ALBUM_ID=\"${ALBUM_ID}\"" >> ~/.profile
            dialog --title "SUCESSO" --msgbox "Variáveis adicionadas a ~/.profile. Faça 'source ~/.profile' ou abra um novo terminal." 10 70
        fi
    else
        dialog --title "INCOMPATÍVEL" --msgbox "Deteção: sistema não é Debian. Esta funcionalidade só grava variáveis permanentes em Debian." 10 70
    fi
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

# Se quiser carregar as variáveis no ambiente actual da shell,
# deve 'source' este ficheiro em vez de o executar.
. "$CONFIG_FILE"

# Oferece opção de tornar as variáveis permanentes no SO
persist_env_vars

# --- 3. FINALIZAÇÃO ---
echo "As configurações foram guardadas em '$CONFIG_FILE'."